from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.messages import Messages
from utils.emojis import Emojis


def get_pesar_keyboard(chat_id, user_id=None, current_view='local'):
    # Pesagem unificada: não há mais toggle Local/Global (global = MAX temporada
    # derivado do local). O quick-button pós-pesagem é só o Ranking.
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=Messages.Pesar.BTN_RANKING,
            callback_data=f"pesar_btn:ranking:{chat_id}",
            icon_custom_emoji_id=Emojis.ID_TROFEU,
            style="success",
        ),
    )
    return builder.as_markup()
