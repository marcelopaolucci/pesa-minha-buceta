from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.messages import Messages
from utils.emojis import Emojis


def get_donate_confirm_keyboard():
    btn_confirm = InlineKeyboardButton(
        text=Messages.Donate.BTN_CONFIRM,
        callback_data="dar_confirm",
        icon_custom_emoji_id=Emojis.ID_DUEL_ACCEPT,
        style="success"
    )
    btn_cancel = InlineKeyboardButton(
        text=Messages.Donate.BTN_CANCEL,
        callback_data="dar_cancel",
        icon_custom_emoji_id=Emojis.ID_DUEL_CANCEL,
        style="danger"
    )
    return InlineKeyboardMarkup(inline_keyboard=[[btn_confirm, btn_cancel]])
