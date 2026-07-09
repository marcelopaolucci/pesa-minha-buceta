import random
import logging
import asyncio
from aiogram import types
from aiogram.filters import CommandObject
from database import transfer_donation, increment_stat, get_peso_legado_or_none
from utils import is_group_chat, format_name, parse_weight_to_grams, strip_html, format_weight
from utils.messages import Messages
from utils.achievements_manager import check_achievements
from utils.keyboards import get_donate_confirm_keyboard

DONATE_EXPIRE_TIME = 60

# {msg_id: {donor_id, receiver_id, receiver_name, chat_id, valor_doacao, kg_display}}
_pending_donations: dict = {}
_background_tasks: set = set()


async def _expire_donation(msg: types.Message, msg_id: int):
    await asyncio.sleep(DONATE_EXPIRE_TIME)
    pending = _pending_donations.pop(msg_id, None)
    if pending:
        try:
            text = Messages.Donate.build_expired_msg(
                donor=format_name(pending["donor_name"]),
                receiver=format_name(pending["receiver_name"]),
            )
            await msg.edit_text(text, parse_mode='HTML', reply_markup=None)
        except Exception:
            pass


async def cmd_doar(message: types.Message, command: CommandObject = None):
    """/dar <peso> (reply) — solicita confirmação antes de transferir peso_legado."""
    if not await is_group_chat(message.chat):
        await message.reply(Messages.Errors.ONLY_GROUP, parse_mode='HTML')
        return

    if not message.reply_to_message:
        await message.reply(Messages.Donate.NO_TARGET, parse_mode='HTML')
        return

    if not message.from_user:
        return
    if not message.reply_to_message.from_user:
        await message.reply(Messages.Errors.BOTS_NO_BCT_MSG, parse_mode='HTML')
        return

    args = command.args if command else None
    if not args:
        await message.reply(Messages.Donate.WEIGHT_NOT_INFORMED, parse_mode='HTML')
        return

    try:
        valor_doacao = parse_weight_to_grams(args)
    except (ValueError, TypeError):
        await message.reply(Messages.Donate.INVALID_WEIGHT, parse_mode='HTML')
        return

    donor_id = message.from_user.id
    receiver = message.reply_to_message.from_user
    receiver_id = receiver.id

    if donor_id == receiver_id:
        await message.reply(Messages.Errors.NO_SELF_DONATE, parse_mode='HTML')
        return

    if receiver.is_bot:
        if receiver.id == message.bot.id:
            await message.reply(Messages.Donate.BOT_RECEIVER, parse_mode='HTML')
        else:
            await message.reply(Messages.Errors.BOTS_NO_BCT_MSG, parse_mode='HTML')
        return

    chat_id = message.chat.id
    balance = await get_peso_legado_or_none(donor_id, chat_id)
    if balance is None:
        await message.reply(random.choice(Messages.Donate.NOT_WEIGHED), parse_mode='HTML')
        return
    kg_to_donate = valor_doacao / 1000.0
    kg_display = f"<b>{valor_doacao:g}g</b>" if valor_doacao < 1000 else f"<b>{kg_to_donate:g}kg</b>"
    if balance < valor_doacao:
        await message.reply(Messages.Donate.build_insufficient_msg(format_weight(balance)), parse_mode='HTML')
        return

    confirm_text = Messages.Donate.build_confirm_msg(
        donor=format_name(message.from_user.first_name),
        receiver=format_name(receiver.first_name),
        kg=kg_display,
    )
    msg = await message.reply(confirm_text, parse_mode='HTML', reply_markup=get_donate_confirm_keyboard())

    _pending_donations[msg.message_id] = {
        "donor_id": donor_id,
        "donor_name": message.from_user.first_name,
        "receiver_id": receiver_id,
        "receiver_name": receiver.first_name,
        "chat_id": message.chat.id,
        "valor_doacao": valor_doacao,
        "kg_display": kg_display,
    }

    task = asyncio.create_task(_expire_donation(msg, msg.message_id))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


async def callback_dar(callback: types.CallbackQuery):
    """Callback dos botões Confirmar/Cancelar da doação."""
    action = callback.data  # "dar_confirm" ou "dar_cancel"
    msg_id = callback.message.message_id
    clicker_id = callback.from_user.id

    pending = _pending_donations.get(msg_id)
    if not pending:
        await callback.answer("Essa doação já expirou.", show_alert=True)
        return

    if clicker_id != pending["donor_id"]:
        await callback.answer(strip_html(Messages.Donate.NOT_AUTHORIZED), show_alert=True)
        return

    del _pending_donations[msg_id]

    if action == "dar_cancel":
        try:
            await callback.message.edit_text(Messages.Donate.CONFIRM_CANCELLED, parse_mode='HTML', reply_markup=None)
        except Exception:
            pass
        await callback.answer(strip_html(Messages.Donate.CONFIRM_CANCELLED))
        return

    # dar_confirm — executa transferência
    donor_id = pending["donor_id"]
    receiver_id = pending["receiver_id"]
    receiver_name = pending["receiver_name"]
    chat_id = pending["chat_id"]
    valor_doacao = pending["valor_doacao"]
    kg_display = pending["kg_display"]
    kg_to_donate = valor_doacao / 1000.0

    result = await transfer_donation(donor_id, receiver_id, chat_id, valor_doacao)

    if result["status"] == "donor_not_weighed":
        await callback.message.edit_text(random.choice(Messages.Donate.NOT_WEIGHED), parse_mode='HTML', reply_markup=None)
        await callback.answer()
        return
    if result["status"] == "insufficient":
        await callback.message.edit_text(Messages.Donate.build_insufficient_msg(format_weight(result["balance"])), parse_mode='HTML', reply_markup=None)
        await callback.answer()
        return
    if result["status"] == "receiver_not_weighed":
        text = random.choice(Messages.Donate.RECEIVER_NOT_WEIGHED).format(receiver=receiver_name)
        await callback.message.edit_text(text, parse_mode='HTML', reply_markup=None)
        await callback.answer()
        return

    await increment_stat(donor_id, chat_id, "donations_made")
    await increment_stat(donor_id, chat_id, "kg_donated", increment=kg_to_donate)
    await check_achievements(
        donor_id, chat_id, "donate",
        bot=callback.bot,
        context={"receiver_weight_before": result["receiver_weight_before"]}
    )

    logging.info(f"Doação Confirmada: {donor_id} -> {receiver_id} ({kg_to_donate}kg)")

    donor_name = format_name(callback.from_user.first_name)
    success_text = Messages.Donate.get_donate_msg(donor=donor_name, receiver=format_name(receiver_name), kg=kg_display)
    await callback.message.edit_text(success_text, parse_mode='HTML', reply_markup=None)
    await callback.answer()
