from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.messages import Messages
from utils.emojis import Emojis


def get_duel_keyboard():
    btn_accept = InlineKeyboardButton(
        text=Messages.Duel.BTN_ACCEPT,
        callback_data="duel_accept",
        icon_custom_emoji_id=Emojis.ID_DUEL_ACCEPT,
        style="success"
    )
    btn_cancel = InlineKeyboardButton(
        text=Messages.Duel.BTN_CANCEL,
        callback_data="duel_cancel",
        icon_custom_emoji_id=Emojis.ID_DUEL_CANCEL,
        style="danger"
    )
    return InlineKeyboardMarkup(inline_keyboard=[[btn_accept, btn_cancel]])
