import time
import logging
import secrets
import asyncio
from aiogram import types
from database import save_duel, get_duel, delete_duel, increment_stat, get_peso_legado, get_peso_legado_or_none, get_duel_cooldown, set_duel_cooldown, transfer_duel_weight
from utils import format_weight, is_group_chat, format_name, strip_html
from utils.messages import Messages
from utils.achievements_manager import check_achievements
from utils.emojis import Emojis
from utils.keyboards import get_duel_keyboard

DUEL_EXPIRE_TIME = 60
DUEL_COOLDOWN = 10
STAKE = 2500.0

# Mantém referência forte para tasks de background — evita GC prematuro antes do sleep terminar.
_background_tasks: set = set()


async def cmd_duelar(message: types.Message):
    """/duelar — desafia o grupo a um duelo de peso (stake: 2.5kg legado, expira em 60s)."""
    if not await is_group_chat(message.chat):
        await message.reply(Messages.Errors.ONLY_GROUP, parse_mode='HTML')
        return

    if not message.from_user:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    now = time.time()

    last_duel = await get_duel_cooldown(user_id, chat_id)
    if last_duel and now - last_duel < DUEL_COOLDOWN:
        remaining = int(DUEL_COOLDOWN - (now - last_duel))
        await message.reply(Messages.Duel.get_random('COOLDOWN_PHRASES', seconds=remaining), parse_mode='HTML')
        return

    peso = await get_peso_legado(user_id, chat_id)
    if peso < STAKE:
        await message.reply(Messages.Errors.NOT_ENOUGH_WEIGHT.format(weight=Messages.Duel.STAKE_DISPLAY), parse_mode='HTML')
        return

    msg_text = Messages.Duel.build_start_msg(
        challenger_name=format_name(user_name),
        stake_display=Messages.Duel.STAKE_DISPLAY,
        seconds=DUEL_EXPIRE_TIME
    )

    msg = await message.reply(msg_text, parse_mode="HTML", reply_markup=get_duel_keyboard())

    await save_duel(
        message_id=msg.message_id,
        challenger_id=user_id,
        challenger_name=user_name,
        chat_id=chat_id,
        stake=STAKE,
        timestamp=int(now)
    )
    await set_duel_cooldown(user_id, chat_id, int(now))

    task = asyncio.create_task(auto_delete_duel(msg, DUEL_EXPIRE_TIME))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


async def auto_delete_duel(msg: types.Message, delay: int):
    """Aguarda timeout e edita a mensagem de duelo para expirado se ainda não foi aceito."""
    await asyncio.sleep(delay)
    duel = await get_duel(msg.message_id)
    if duel:
        await delete_duel(msg.message_id)
        try:
            await msg.edit_text(Messages.Duel.EXPIRED_MESSAGE, parse_mode='HTML', reply_markup=None)
        except Exception:
            pass


async def callback_duelo(callback: types.CallbackQuery):
    """Callback dos botões Aceitar/Cancelar duelo."""
    action = callback.data.removeprefix("duel_")
    target_msg_id = callback.message.message_id

    duel = await get_duel(target_msg_id)
    if not duel:
        await callback.answer(Messages.Duel.EXPIRED_POPUP, show_alert=True)
        try:
            await callback.message.delete()
        except Exception:
            pass
        return

    challenger_id = duel["challenger_id"]
    challenger_name = duel["challenger_name"]
    chat_id = duel["chat_id"]
    acceptor_id = callback.from_user.id
    acceptor_name = callback.from_user.first_name

    if action == "cancel":
        if acceptor_id != challenger_id:
            await callback.answer(strip_html(Messages.Duel.CALLBACK_NOT_AUTHORIZED), show_alert=True)
            return
        await delete_duel(target_msg_id)
        try:
            await callback.message.edit_text(Messages.Duel.CALLBACK_CANCELLED, parse_mode="HTML", reply_markup=None)
        except Exception:
            pass
        await callback.answer(strip_html(Messages.Duel.CALLBACK_CANCELLED))
        return

    # action == "accept"
    if time.time() - duel["timestamp"] > DUEL_EXPIRE_TIME:
        await delete_duel(target_msg_id)
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.answer(Messages.Duel.EXPIRED_POPUP_SHORT, show_alert=True)
        return

    if acceptor_id == challenger_id:
        await callback.answer(strip_html(Messages.Errors.NO_SELF_DUEL), show_alert=True)
        return

    acceptor_weight = await get_peso_legado_or_none(acceptor_id, chat_id)
    if acceptor_weight is None:
        await callback.answer(strip_html(Messages.Errors.NOT_REGISTERED), show_alert=True)
        return
    if acceptor_weight < STAKE:
        await callback.answer(strip_html(Messages.Errors.NOT_ENOUGH_WEIGHT.format(weight=Messages.Duel.STAKE_DISPLAY)), show_alert=True)
        return

    challenger_weight = await get_peso_legado_or_none(challenger_id, chat_id)
    if challenger_weight is None or challenger_weight < STAKE:
        await delete_duel(target_msg_id)
        await callback.message.edit_text(Messages.Duel.CALLBACK_CREATOR_POOR, parse_mode='HTML', reply_markup=None)
        return

    await delete_duel(target_msg_id)
    winner_side = secrets.choice(["challenger", "acceptor"])

    if winner_side == "challenger":
        winner_id, winner_name = challenger_id, challenger_name
        loser_id, loser_name = acceptor_id, acceptor_name
        winner_weight, loser_weight = challenger_weight, acceptor_weight
    else:
        winner_id, winner_name = acceptor_id, acceptor_name
        loser_id, loser_name = challenger_id, challenger_name
        winner_weight, loser_weight = acceptor_weight, challenger_weight

    await transfer_duel_weight(winner_id, loser_id, chat_id, STAKE)

    await increment_stat(winner_id, chat_id, "duels_won")
    await increment_stat(loser_id, chat_id, "duels_lost")

    await check_achievements(
        winner_id, chat_id, "duel_result",
        bot=callback.bot,
        context={"was_win": True, "opponent_weight": loser_weight, "winner_weight_before": winner_weight}
    )
    await check_achievements(loser_id, chat_id, "duel_result", bot=callback.bot)

    logging.info(f"Duelo finalizado: {winner_name} venceu {loser_name} no chat {chat_id}")

    await callback.message.edit_text(
        Messages.Duel.build_end_msg(
            challenger_name=format_name(challenger_name),
            acceptor_name=format_name(acceptor_name),
            winner_name=format_name(winner_name),
            loser_name=format_name(loser_name),
            stake_display=Messages.Duel.STAKE_DISPLAY
        ),
        parse_mode="HTML",
        reply_markup=None
    )
    await callback.answer(strip_html(Messages.Duel.CALLBACK_SUCCESS_POPUP))
