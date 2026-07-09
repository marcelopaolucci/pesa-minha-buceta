import html
import logging
from aiogram import types
from database import reset_user
from utils.messages import Messages
from utils import is_group_chat
import config


async def cmd_resetarbct(message: types.Message):
    """/resetarbct (reply) — admins e criadores do grupo podem zerar buceta de um usuário."""
    if not message.from_user:
        return

    sender_id = message.from_user.id
    is_owner = sender_id == config.ALLOWED_USER_ID

    if not is_owner:
        if not await is_group_chat(message.chat):
            await message.reply(Messages.Reset.ARBCT_ONLY_GROUP, parse_mode='HTML')
            return
        chat_member = await message.bot.get_chat_member(message.chat.id, sender_id)
        if chat_member.status not in ["administrator", "creator"]:
            await message.reply(Messages.Reset.ARBCT_ADMIN_ONLY, parse_mode='HTML')
            return

    logging.debug(f"DEBUG_RESET: Reply to message object: {message.reply_to_message}")

    if not message.reply_to_message:
        await message.reply(Messages.Reset.ARBCT_NEED_REPLY, parse_mode='HTML')
        return

    alvo = message.reply_to_message.from_user
    if not alvo:
        logging.debug(f"DEBUG_RESET: Reply detectado, mas from_user é NULO. Objeto: {message.reply_to_message}")
        await message.reply(Messages.Reset.ARBCT_NEED_REPLY, parse_mode='HTML')
        return

    logging.info(f"Admin {sender_id} resetando buceta do alvo {alvo.id} ({alvo.first_name}) no chat {message.chat.id}")

    await reset_user(alvo.id, message.chat.id)
    await message.reply(
        Messages.Reset.ARBCT_SUCCESS.format(name=html.escape(alvo.first_name or alvo.username or "")),
        parse_mode='HTML'
    )
