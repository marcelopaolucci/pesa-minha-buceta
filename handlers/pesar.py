from datetime import datetime
from aiogram import types
from database import exec_pesar_transaction, get_user_meta, get_user_name, increment_stat, get_today_weight_change
from utils import (format_weight, time_until_next_update, is_group_chat, roll_weighted_kg,
                   get_streak_multiplier, format_gain, format_name, simulate_streak,
                   safe_edit, parse_cb, display_name, ANON)
from utils.messages import Messages
from utils.achievements_manager import check_achievements
from utils.keyboards import get_pesar_keyboard, get_combined_ranking_keyboard
from handlers.ranking import build_combined_ranking_text
from services.profile import get_profile_snapshot, build_profile_text


async def cmd_pesar(message: types.Message):
    """/pesar — pesagem diária do usuário no grupo. 1x/dia por usuário por grupo."""
    if not await is_group_chat(message.chat):
        await message.reply(Messages.Errors.ONLY_GROUP, parse_mode='HTML')
        return

    if not message.from_user:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    display_name = message.from_user.first_name

    meta = await get_user_meta(user_id, chat_id)
    multiplier = get_streak_multiplier(simulate_streak(meta["last_date"], meta["streak"]))

    roll = roll_weighted_kg(meta["pity"])
    peso_final = round(roll["peso_base"] * multiplier, 2)

    result = await exec_pesar_transaction(
        user_id, chat_id,
        f"@{message.from_user.username}" if message.from_user.username else None,
        message.from_user.first_name or "",
        message.from_user.last_name or "",
        message.chat.title or "",
        f"@{message.chat.username}" if message.chat.username else None,
        roll["tier"], roll["peso_base"], peso_final
    )

    keyboard = get_pesar_keyboard(chat_id, user_id, current_view='local')

    if result["status"] == "cooldown":
        time_left = time_until_next_update()
        kg_today = await get_today_weight_change(user_id, chat_id)
        if kg_today is not None:
            cooldown_text = Messages.Pesar.get_cooldown_recap(
                name=format_name(display_name),
                context="locais",
                kg=format_gain(kg_today / 1000),
                time_left=time_left
            )
        else:
            cooldown_text = Messages.Pesar.COOLDOWN.format(name=display_name, time_left=time_left)
        await message.reply(cooldown_text, parse_mode='HTML', reply_markup=keyboard)
        return

    pesar_text = Messages.Pesar.get_pesar_msg(
        name=format_name(display_name),
        kg=format_gain(result['kg']),
        new_weight=format_weight(result['new_weight']),
        new_legado=format_weight(result['new_legado']),
        tier=result['tier'],
        streak=result['streak']
    )
    # Virada de temporada: o 1º /pesar do grupo na nova season dispara o reset
    # lazy e devolve os campeões da temporada encerrada. Anuncia uma vez no grupo.
    reset_announcement = result.get("reset_announcement")
    if reset_announcement:
        await message.answer(
            Messages.Ranking.get_reset_announcement_msg(result["season_label"], reset_announcement),
            parse_mode='HTML'
        )

    promo_suffix = ""
    if datetime(2026, 6, 1, 0, 0, 0) <= datetime.now() < datetime(2026, 7, 1, 0, 0, 0):
        promo_suffix = '\n\n🎬 <a href="https://t.me/framegrambot">@framegrambot</a> — Adivinhe o filme ou série pelo frame. Um desafio por dia.'
    await message.reply(
        pesar_text + promo_suffix,
        parse_mode='HTML',
        reply_markup=keyboard
    )

    await increment_stat(user_id, chat_id, "total_weighs")
    new_max_streak = max(meta["max_streak"], result["streak"])
    await check_achievements(user_id, chat_id, "weigh", bot=message.bot, context={
        "max_streak": new_max_streak,
    })


async def on_pesar_btn_ranking(callback: types.CallbackQuery):
    """Callback do botão Ranking nos quick-buttons do /pesar."""
    cb = parse_cb(callback.data, "_action", "int:chat_id")
    if cb is None:
        return await callback.answer()

    text = await build_combined_ranking_text(cb["chat_id"], callback.message.chat.title)
    kb = get_combined_ranking_keyboard(cb["chat_id"], 'local')
    await safe_edit(callback, text, reply_markup=kb)
    await callback.answer()


async def on_pesar_btn_perfil(callback: types.CallbackQuery):
    """Callback do botão Perfil nos quick-buttons do /pesar."""
    cb = parse_cb(callback.data, "_action", "int:user_id", "int:chat_id")
    if cb is None:
        return await callback.answer()

    user_id, chat_id = cb["user_id"], cb["chat_id"]
    name = await get_user_name(user_id, chat_id)
    snapshot = await get_profile_snapshot(user_id, chat_id)
    await callback.message.answer(
        build_profile_text(snapshot, name, callback.message.chat.title or ""),
        parse_mode='HTML'
    )
    await callback.answer()
