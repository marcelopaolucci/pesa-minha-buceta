import html
import logging
import random
from aiogram import types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_total_system_data, update_activity, get_user_name
from utils import is_group_chat, safe_edit, parse_cb
from utils.messages import Messages
from utils.emojis import Emojis
from utils.keyboards import get_perfil_keyboard
from services.bot_cache import get_bot_me
from services.profile import (get_profile_snapshot, build_profile_text,
                               get_global_profile_snapshot, build_global_profile_text)


async def cmd_perfil(message: Message):
    """/perfil — exibe perfil do usuário (ou do alvo via reply). Reply no bot exibe easter egg de stats globais."""
    if not await is_group_chat(message.chat):
        await message.reply(Messages.Errors.ONLY_GROUP, parse_mode="HTML")
        return

    if not message.from_user:
        return

    await update_activity(
        message.from_user.id,
        message.chat.id,
        username=f"@{message.from_user.username}" if message.from_user.username else None,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    target = (
        message.reply_to_message.from_user
        if message.reply_to_message and message.reply_to_message.from_user
        else message.from_user
    )

    if target.is_bot:
        bot_info = await get_bot_me(message.bot)
        if target.id == bot_info.id:
            try:
                sys_data = await get_total_system_data()
                profile_text = Messages.Profile.get_bot_profile_text(
                    name=html.escape(target.first_name),
                    total_kg=f"{sys_data['total_kg']:,.2f}",
                    total_users=sys_data['total_users'],
                    total_groups=sys_data['total_groups']
                )
                markup = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text=Messages.Help.BTN_CONTACT,
                        url="https://t.me/centraldabuceta",
                        style="success",
                        icon_custom_emoji_id=Emojis.ID_SUPORTE
                    )
                ]])
                await message.reply(profile_text, parse_mode="HTML", reply_markup=markup)
            except Exception as e:
                logging.exception(f"Erro no Easter Egg do Perfil: {e}")
                await message.reply(Messages.Errors.SELF_BOT_MSG(), parse_mode="HTML")
        else:
            await message.reply(Messages.Errors.BOTS_NO_BCT_MSG, parse_mode="HTML")
        return

    snapshot = await get_profile_snapshot(target.id, message.chat.id)
    local_empty = snapshot["peso_legado"] == 0.0 and snapshot["peso_temporada"] == 0.0

    if local_empty:
        global_snap = await get_global_profile_snapshot(target.id)
        global_empty = global_snap["peso_legado"] == 0.0 and global_snap["peso_temporada"] == 0.0

        if global_empty and target.id != message.from_user.id:
            await message.reply(Messages.Profile.NOT_REGISTERED_YET, parse_mode="HTML")
            return

        if not global_empty:
            keyboard = get_perfil_keyboard(message.chat.id, target.id, current_view='global')
            await message.reply(
                build_global_profile_text(global_snap, target.first_name),
                parse_mode="HTML",
                reply_markup=keyboard
            )
            return

    keyboard = get_perfil_keyboard(message.chat.id, target.id, current_view='local')
    await message.reply(
        build_profile_text(snapshot, target.first_name, message.chat.title),
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def on_perfil_btn_local(callback: types.CallbackQuery):
    """Callback botão Local no perfil — exibe perfil local."""
    cb = parse_cb(callback.data, "_action", "int:chat_id", "int:user_id")
    if cb is None:
        return await callback.answer()

    chat_id, user_id = cb["chat_id"], cb["user_id"]
    name = await get_user_name(user_id, chat_id)
    snapshot = await get_profile_snapshot(user_id, chat_id)
    keyboard = get_perfil_keyboard(chat_id, user_id, current_view='local')
    await safe_edit(
        callback,
        build_profile_text(snapshot, name, callback.message.chat.title or ""),
        reply_markup=keyboard,
    )
    await callback.answer()


async def on_perfil_btn_global(callback: types.CallbackQuery):
    """Callback botão Global no perfil — exibe perfil global agregado."""
    cb = parse_cb(callback.data, "_action", "int:chat_id", "int:user_id")
    if cb is None:
        return await callback.answer()

    chat_id, user_id = cb["chat_id"], cb["user_id"]
    name = await get_user_name(user_id, chat_id)
    snapshot = await get_global_profile_snapshot(user_id)
    keyboard = get_perfil_keyboard(chat_id, user_id, current_view='global')
    await safe_edit(callback, build_global_profile_text(snapshot, name), reply_markup=keyboard)
    await callback.answer()
