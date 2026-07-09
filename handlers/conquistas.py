import html
import logging
from aiogram import types
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_global_achievements_list
from utils import is_group_chat
from utils.messages import Messages
from utils.achievements_manager import ACHIEVEMENTS_DEFS, AchievementTiers
from utils.emojis import Emojis
from services.bot_cache import get_bot_me

_URL_GRIMORIO = "https://telegra.ph/Grim%C3%B3rio-de-Conquistas-do-Pesa-Minha-Buceta-03-31"


def get_progress_bar(current, total, length=10):
    """Barra visual de progresso em blocos █/░."""
    if total == 0:
        return "░" * length
    filled = round((current / total) * length)
    return "█" * filled + "░" * (length - filled)


async def cmd_conquistas(message: types.Message):
    """/conquistas — envia Grimório no PV quando chamado de grupo; exibe inline no PV."""
    if not message.from_user:
        return
    target = message.from_user
    if target.is_bot:
        bot_info = await get_bot_me(message.bot)
        is_self = target.id == bot_info.id
        msg = Messages.Errors.SELF_BOT_MSG() if is_self else Messages.Errors.BOTS_NO_BCT_MSG
        await message.reply(msg, parse_mode='HTML')
        return

    is_group = await is_group_chat(message.chat)
    if not is_group:
        await show_conquistas_logic(message, user_override=target, view_mode='personal')
        return

    # Grupo: tenta enviar Grimório no PV do usuário
    bot_info = await get_bot_me(message.bot)
    pv_msg, pv_markup = await _build_conquistas_payload(
        message, user=target, bot_username=bot_info.username
    )
    try:
        await message.bot.send_message(
            chat_id=target.id,
            text=pv_msg,
            parse_mode='HTML',
            reply_markup=pv_markup,
        )
        await message.reply(Messages.Achievements.SENT_TO_PV, parse_mode='HTML')
    except (TelegramForbiddenError, TelegramBadRequest):
        no_pv_markup = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=Messages.Achievements.BTN_ABRIR_PV,
                url=f"https://t.me/{bot_info.username}?start=conquistas",
            )
        ]])
        await message.reply(Messages.Achievements.NO_PV, parse_mode='HTML', reply_markup=no_pv_markup)


async def callback_show_achievements(callback_query: types.CallbackQuery):
    """Callback do botão 'ver conquistas' no /pesar ou /perfil."""
    await show_conquistas_logic(callback_query.message, user_override=callback_query.from_user, view_mode='personal')
    await callback_query.answer()


async def process_achievements_callback(callback_query: types.CallbackQuery):
    """Callback de navegação entre páginas/views do Grimório."""
    parts = callback_query.data.split(':')
    # Formato: achievements_page:VIEW:USER:CHAT:PAGE
    if len(parts) >= 3:
        view_mode = parts[1]
        await show_conquistas_logic(
            callback_query.message,
            user_override=callback_query.from_user,
            view_mode=view_mode,
            is_edit=True,
        )
    await callback_query.answer()


def _build_conquistas_markup(unlocked_count, missing_count, view_mode):
    """Teclado padrão: [Tem X] [Falta X] + [Grimório] abaixo."""
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=Messages.Achievements.BTN_TEM.format(count=unlocked_count),
                callback_data="achievements_page:personal:0:0:0",
                style="success" if view_mode == 'personal' else None,
                icon_custom_emoji_id=Emojis.ID_DUEL_ACCEPT
            ),
            InlineKeyboardButton(
                text=Messages.Achievements.BTN_FALTA.format(count=missing_count),
                callback_data="achievements_page:missing:0:0:0",
                style="danger" if view_mode == 'missing' else None,
                icon_custom_emoji_id=Emojis.ID_CADEADO
            ),
        ],
        [
            InlineKeyboardButton(
                text=Messages.Achievements.BTN_GRIMORIO,
                url=_URL_GRIMORIO,
                style="primary",
                icon_custom_emoji_id=Emojis.ID_LIVRO
            )
        ]
    ])
    return markup


async def _build_conquistas_payload(message, user, chat_id=None, bot_username=None, view_mode='personal'):
    """Monta texto e markup do Grimório para um usuário. Retorna (text, markup)."""
    display_name = user.first_name
    _all_ids = set(await get_global_achievements_list(user.id))
    unlocked_ids = _all_ids & set(ACHIEVEMENTS_DEFS.keys())
    total_achievements = len(ACHIEVEMENTS_DEFS)
    unlocked_count = len(unlocked_ids)
    missing_count = total_achievements - unlocked_count

    markup = _build_conquistas_markup(unlocked_count, missing_count, view_mode)
    pct = int((unlocked_count / total_achievements) * 100) if total_achievements else 0
    bar = get_progress_bar(unlocked_count, total_achievements)

    if view_mode == 'missing':
        msg = f"{Emojis.TRANCADO} <b>CONQUISTAS PENDENTES — {display_name.upper()}</b>\n"
        msg += Messages.Achievements.PROGRESS.format(count=unlocked_count, total=total_achievements, bar=bar, pct=pct) + "\n\n"
        categories = {
            f"{Emojis.PESO} Pesagem": [],
            f"{Emojis.FOGO} Sequência": [],
            f"{Emojis.CALENDARIO} Assiduidade": [],
            f"{Emojis.ESPADA} Duelos": [],
            f"{Emojis.PRESENTE} Doações": [],
            f"{Emojis.ESTRELA} Buceta do Dia": [],
            f"{Emojis.TIMER} Horário": [],
            f"{Emojis.PLANETA} Grupos": [],
        }
        _cat_map = {
            f"{Emojis.PESO} Pesagem": lambda k: k.startswith('bcto_'),
            f"{Emojis.FOGO} Sequência": lambda k: k.startswith('streak_'),
            f"{Emojis.CALENDARIO} Assiduidade": lambda k: k == 'first_weigh' or k.startswith('weigh_'),
            f"{Emojis.ESPADA} Duelos": lambda k: k == 'first_duel' or k.startswith('duels_'),
            f"{Emojis.PRESENTE} Doações": lambda k: k == 'first_donate' or k.startswith('donated_'),
            f"{Emojis.ESTRELA} Buceta do Dia": lambda k: k.startswith('bct_dia_'),
            f"{Emojis.TIMER} Horário": lambda k: k.startswith('hora_') or k.startswith('hour_'),
            f"{Emojis.PLANETA} Grupos": lambda k: k.startswith(('nomade_', 'expansion_', 'queen_', 'monopoly_')),
        }
        _tier_order = {AchievementTiers.BRONZE: 0, AchievementTiers.SILVER: 1, AchievementTiers.GOLD: 2, AchievementTiers.PLATINUM: 3}
        for ach_id, ach in ACHIEVEMENTS_DEFS.items():
            if ach_id not in unlocked_ids:
                for cat_label, matcher in _cat_map.items():
                    if matcher(ach_id):
                        categories[cat_label].append((ach["tier"], ach["name"]))
                        break
        for cat_label, entries in categories.items():
            if entries:
                msg += f"<blockquote expandable><b>{cat_label}:</b>\n"
                for _, name in sorted(entries, key=lambda x: _tier_order.get(x[0], 99)):
                    msg += f" • {name}\n"
                msg += "</blockquote>"
        return msg, markup

    # view_mode == 'personal'
    msg = Messages.Achievements.HEADER_PANTEAO.format(name=display_name.upper()) + "\n"
    msg += Messages.Achievements.PROGRESS.format(count=unlocked_count, total=total_achievements, bar=bar, pct=pct) + "\n\n"

    if not unlocked_ids:
        safe_name = f"<b>{html.escape(display_name)}</b>"
        msg += f"<i>{Messages.Achievements.EMPTY.format(name=safe_name)}</i>\n\n"
    else:
        tiers = {
            AchievementTiers.PLATINUM: [],
            AchievementTiers.GOLD: [],
            AchievementTiers.SILVER: [],
            AchievementTiers.BRONZE: [],
        }
        for ach_id in unlocked_ids:
            if ach_id in ACHIEVEMENTS_DEFS:
                ach = ACHIEVEMENTS_DEFS[ach_id]
                tiers[ach["tier"]].append(ach["name"])
        for tier_label, names in tiers.items():
            if names:
                msg += f"<blockquote expandable><b>{tier_label}:</b>\n"
                for name in sorted(names):
                    msg += f" • {name}\n"
                msg += "</blockquote>"

    return msg, markup




async def show_conquistas_logic(
    message: types.Message,
    user_override=None,
    view_mode='personal',
    is_edit=False,
):
    """Renderiza e envia/edita o Grimório de conquistas."""
    user = user_override or message.from_user

    msg, markup = await _build_conquistas_payload(message, user=user, view_mode=view_mode)

    try:
        if is_edit:
            await message.edit_text(msg, parse_mode='HTML', reply_markup=markup)
        else:
            await message.reply(msg, parse_mode='HTML', reply_markup=markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return
        logging.error(f"Erro ao enviar Grimório: {e}")
    except Exception as e:
        logging.error(f"Erro ao enviar Grimório: {e}")
