from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.messages import Messages
from utils.emojis import Emojis


def get_perfil_keyboard(chat_id, user_id, current_view='local'):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=Messages.Pesar.BTN_LOCAL,
            callback_data=f"perfil_btn:local:{chat_id}:{user_id}",
            icon_custom_emoji_id=Emojis.ID_LOCAL_HEADER,
            style="danger" if current_view == 'local' else None,
        ),
        InlineKeyboardButton(
            text=Messages.Ranking.BTN_GLOBAL,
            callback_data=f"perfil_btn:global:{chat_id}:{user_id}",
            icon_custom_emoji_id=Emojis.ID_PLANETA,
            style="primary" if current_view == 'global' else None,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=Messages.Pesar.BTN_RANKING,
            callback_data=f"rank2:local:{chat_id}",
            icon_custom_emoji_id=Emojis.ID_TROFEU,
            style="success",
        )
    )
    return builder.as_markup()
