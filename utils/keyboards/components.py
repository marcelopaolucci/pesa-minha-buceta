"""
Componentes reutilizáveis de UI (botões inline).
Centraliza estilos e ícones que se repetem em múltiplos teclados.
"""
from typing import Optional
from aiogram.types import InlineKeyboardButton
from utils.messages import Messages
from utils.emojis import Emojis


def add_to_group_button(
    bot_username: str,
    *,
    label: Optional[str] = None,
    use_static: bool = False,
) -> InlineKeyboardButton:
    """Botão 'Adicionar ao Grupo' padrão (estilo danger, ícone foguete)."""
    return InlineKeyboardButton(
        text=label or Messages.Global.BTN_ADD_GROUP,
        url=f"https://t.me/{bot_username}?startgroup=true",
        icon_custom_emoji_id=None if use_static else Emojis.ID_FOGUETE,
        style="danger",
    )


def support_button(*, use_static: bool = False) -> InlineKeyboardButton:
    """Botão 'Suporte' padrão (estilo success, ícone suporte)."""
    return InlineKeyboardButton(
        text=Messages.Help.BTN_CONTACT,
        url="https://t.me/centraldabuceta",
        icon_custom_emoji_id=None if use_static else Emojis.ID_SUPORTE,
        style="success",
    )


def back_button(callback_data: str, *, label: Optional[str] = None) -> InlineKeyboardButton:
    """Botão 'Voltar' padrão (estilo primary, ícone voltar)."""
    return InlineKeyboardButton(
        text=label or Messages.Help.BTN_BACK,
        callback_data=callback_data,
        icon_custom_emoji_id=Emojis.ID_VOLTAR,
        style="primary",
    )


def scope_toggle(
    local_cb: str,
    global_cb: str,
    current: str,
) -> tuple[InlineKeyboardButton, InlineKeyboardButton]:
    """
    Par Local/Global com style ativo conforme `current` ('local' | 'global').
    Retorna tupla pra usar com builder.row(*scope_toggle(...)).
    """
    return (
        InlineKeyboardButton(
            text=Messages.Pesar.BTN_LOCAL,
            callback_data=local_cb,
            icon_custom_emoji_id=Emojis.ID_LOCAL_HEADER,
            style="danger" if current == 'local' else None,
        ),
        InlineKeyboardButton(
            text=Messages.Ranking.BTN_GLOBAL,
            callback_data=global_cb,
            icon_custom_emoji_id=Emojis.ID_PLANETA,
            style="primary" if current == 'global' else None,
        ),
    )
