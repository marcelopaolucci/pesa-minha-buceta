from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.messages import Messages
from utils.emojis import Emojis


def get_help_markup(active_page: str = "main", bot_username: str | None = None) -> InlineKeyboardMarkup:
    """Teclado do /ajuda — toggles. Botão ativo fica azul (primary), demais apagados."""

    def section_btn(page_id: str, premium_id: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=" ",
            callback_data=f"help:{page_id}",
            style="success" if active_page == page_id else None,
            icon_custom_emoji_id=premium_id,
        )

    buttons = [
        [
            section_btn("pesar_local",  Emojis.ID_PESO),
            section_btn("pesar_global", Emojis.ID_PLANETA),
            section_btn("bctdodia",     Emojis.ID_BRILHO),
        ],
        [
            section_btn("conquistas",   Emojis.ID_COROA),
            section_btn("ranking",      Emojis.ID_TROFEU),
            section_btn("perfil",       Emojis.ID_PERFIL),
        ],
        [
            section_btn("doar",         Emojis.ID_PRESENTE),
            section_btn("duelo",        Emojis.ID_BOXE),
            section_btn("reset",        Emojis.ID_CLEAN),
        ],
        [
            InlineKeyboardButton(
                text="Adicionar",
                url=f"https://t.me/{bot_username}?startgroup=true",
                style="danger",
                icon_custom_emoji_id="5030787243543888610",
            ),
            InlineKeyboardButton(
                text=Messages.Help.BTN_CONTACT,
                url="https://t.me/centraldabuceta",
                style="primary",
                icon_custom_emoji_id=Emojis.ID_SUPORTE,
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
