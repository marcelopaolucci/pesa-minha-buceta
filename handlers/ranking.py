import html
from aiogram import types
from database import get_leaderboard
from utils import format_weight, is_group_chat, get_next_reset_date, safe_edit, parse_cb, display_name, ANON
from utils.messages import Messages
from services.profile import get_profile_snapshot, get_global_profile_snapshot, build_profile_text, build_global_profile_text
from utils.emojis import Emojis
from utils.keyboards import get_ranking_keyboard, get_combined_ranking_keyboard, get_ranking_back_keyboard

_MEDALHAS = [Emojis.MEDALHA_1, Emojis.MEDALHA_2, Emojis.MEDALHA_3]


def _display_name(username, first_name, last_name) -> str:
    """Nome formatado e HTML-escaped para exibição no ranking."""
    return html.escape(f"{first_name or ''} {last_name or ''}".strip() or username or "")


async def build_ranking_text(ranking_type, chat_id, chat_title, is_global=False):
    """Monta o texto do ranking (temporada ou legado, local ou global)."""
    if is_global:
        column = "peso_legado" if ranking_type == 'legado' else "peso_temporada"
        header = Messages.Ranking.HEADER_GLOBAL_LEGACY if ranking_type == 'legado' else Messages.Ranking.HEADER_GLOBAL_SEASONAL
    else:
        column = "peso_legado" if ranking_type == 'legado' else "peso_temporada"
        header = Messages.Ranking.HEADER_LEGADO if ranking_type == 'legado' else Messages.Ranking.HEADER_TEMPORADA

    data = await get_leaderboard(0 if is_global else chat_id, column=column)
    if not data:
        return Messages.Ranking.EMPTY()

    msg = header.format(chat_title=chat_title)

    for i, (username, first_name, last_name, value) in enumerate(data[:3], 1):
        msg += f"{_MEDALHAS[i - 1]} <b>{_display_name(username, first_name, last_name)}</b> — <b><code>{value / 1000.0:.2f}kg</code></b>\n"

    if data[3:]:
        msg += "\n<blockquote expandable>"
        for i, (username, first_name, last_name, value) in enumerate(data[3:], 4):
            msg += f"<b>{i}.</b> {_display_name(username, first_name, last_name)} — <b><code>{value / 1000.0:.2f}kg</code></b>\n"
        msg += "</blockquote>"

    footer = Messages.Ranking.DESC_LEGADO if ranking_type == 'legado' else Messages.Ranking.get_seasonal_footer()
    msg += f"\n{footer}"

    if is_global:
        msg += Messages.Global.FOOTER_CTA_ADD_GROUP

    return msg


async def build_combined_ranking_text(chat_id: int, chat_title: str, is_global: bool = False) -> str:
    """Ranking combinado: Temporada + Legado em blocos expansíveis.

    Global mostra só Temporada: no modelo unificado o peso global é derivado do
    MAX(peso_temporada) local (get_leaderboard(0, ...)); não há legado global."""
    effective_id = 0 if is_global else chat_id
    temporada_data = await get_leaderboard(effective_id, column="peso_temporada")
    legado_data = None if is_global else await get_leaderboard(effective_id, column="peso_legado")

    context_emoji = Emojis.PLANETA if is_global else Emojis.LOCAL_HEADER
    context_title = html.escape("Telegram Global" if is_global else (chat_title or ""))

    scope = "Global" if is_global else "Local"
    msg = Messages.Ranking.HEADER_COMBINED.format(scope=scope, context_emoji=context_emoji, context_title=context_title)

    def _render_block(data):
        if not data:
            return Messages.Ranking.EMPTY() + "\n"
        block = "<blockquote expandable>"
        for i, (username, first_name, last_name, value) in enumerate(data[:20], 1):
            name = _display_name(username, first_name, last_name)
            kg = f"{value / 1000.0:.2f}kg"
            if i <= 3:
                block += f"{_MEDALHAS[i - 1]} <b>{name}</b> — <b><code>{kg}</code></b>\n"
            else:
                block += f"<b>{i}.</b> {name} — <b><code>{kg}</code></b>\n"
        block += "</blockquote>"
        return block

    msg += Messages.Ranking.SECTION_TEMPORADA
    msg += _render_block(temporada_data)
    if not is_global:
        msg += Messages.Ranking.SECTION_LEGADO
        msg += _render_block(legado_data)

    reset_date = get_next_reset_date().strftime("%d/%m")
    msg += f"\n{Messages.Ranking.FOOTER_COMBINED.format(reset_date=reset_date)}"

    return msg


async def cmd_ranking(message: types.Message):
    """/ranking — exibe ranking combinado (temporada + legado) do grupo."""
    if not await is_group_chat(message.chat):
        await message.reply(Messages.Errors.ONLY_GROUP, parse_mode='HTML')
        return

    chat_id = message.chat.id
    text = await build_combined_ranking_text(chat_id, message.chat.title)
    await message.reply(text, parse_mode='HTML', reply_markup=get_combined_ranking_keyboard(chat_id, 'local'))


async def process_combined_ranking_callback(callback_query: types.CallbackQuery):
    """Callback dos botões Local/Global do ranking combinado (rank2:*)."""
    cb = parse_cb(callback_query.data, "view", "int:chat_id")
    if cb is None:
        return await callback_query.answer(Messages.Ranking.CALLBACK_ERROR)

    view, target_chat_id = cb["view"], cb["chat_id"]
    chat_title = callback_query.message.chat.title or "Ranking"
    if view in ('perfil', 'perfil_local', 'perfil_global'):
        user_id = callback_query.from_user.id
        name = display_name(callback_query.from_user)
        is_perfil_global = (view == 'perfil_global')
        if is_perfil_global:
            snapshot = await get_global_profile_snapshot(user_id)
            text = build_global_profile_text(snapshot, name)
        else:
            snapshot = await get_profile_snapshot(user_id, target_chat_id)
            text = build_profile_text(snapshot, name, chat_title)
        perfil_view = 'global' if is_perfil_global else 'local'
        await safe_edit(
            callback_query, text,
            reply_markup=get_ranking_back_keyboard(target_chat_id, 'local', perfil_view),
        )
        return await callback_query.answer()

    is_global = (view == 'global')
    text = await build_combined_ranking_text(target_chat_id, chat_title, is_global=is_global)
    await safe_edit(callback_query, text, reply_markup=get_combined_ranking_keyboard(target_chat_id, view))
    await callback_query.answer()


async def process_ranking_callback(callback_query: types.CallbackQuery):
    """Callback dos botões Temporada/Legado do ranking interativo."""
    cb = parse_cb(callback_query.data, "action", "int:chat_id")
    if cb is None:
        return await callback_query.answer(Messages.Ranking.CALLBACK_ERROR)

    action, target_chat_id = cb["action"], cb["chat_id"]
    chat_title = callback_query.message.chat.title or "Ranking"
    if action == 'global':
        new_content = await build_ranking_text('temporada', 0, "Mundo", is_global=True)
    else:
        new_content = await build_ranking_text(action, target_chat_id, chat_title)

    await safe_edit(callback_query, new_content, reply_markup=get_ranking_keyboard(action, target_chat_id))
    await callback_query.answer()
