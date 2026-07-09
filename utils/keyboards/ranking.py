from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.messages import Messages
from utils.emojis import Emojis


def get_combined_ranking_keyboard(chat_id: int, current_view: str = 'local'):
    """Teclado do ranking combinado. Perfil apagado por default, acende verde quando ativo."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=Messages.Pesar.BTN_LOCAL,
            callback_data=f"rank2:local:{chat_id}",
            icon_custom_emoji_id=Emojis.ID_LOCAL_HEADER,
            style="danger" if current_view == 'local' else None,
        ),
        InlineKeyboardButton(
            text=Messages.Ranking.BTN_GLOBAL,
            callback_data=f"rank2:global:{chat_id}",
            icon_custom_emoji_id=Emojis.ID_PLANETA,
            style="primary" if current_view == 'global' else None,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=Messages.Pesar.BTN_PERFIL,
            callback_data=f"rank2:perfil:{chat_id}",
            icon_custom_emoji_id=Emojis.ID_PERFIL,
            style="success",
        )
    )
    return builder.as_markup()


def get_ranking_back_keyboard(chat_id: int, back_view: str = 'local', perfil_view: str = 'local'):
    """Teclado quando perfil da pessoa que clicou é exibido a partir do ranking.

    Local/Global aqui togglam entre perfil local e perfil global.
    Voltar retorna ao ranking combinado.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=Messages.Pesar.BTN_LOCAL,
            callback_data=f"rank2:perfil_local:{chat_id}",
            icon_custom_emoji_id=Emojis.ID_LOCAL_HEADER,
            style="danger" if perfil_view == 'local' else None,
        ),
        InlineKeyboardButton(
            text=Messages.Ranking.BTN_GLOBAL,
            callback_data=f"rank2:perfil_global:{chat_id}",
            icon_custom_emoji_id=Emojis.ID_PLANETA,
            style="primary" if perfil_view == 'global' else None,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=Messages.Pesar.BTN_RANKING,
            callback_data=f"rank2:{back_view}:{chat_id}",
            icon_custom_emoji_id=Emojis.ID_TROFEU,
            style="success",
        )
    )
    return builder.as_markup()


def get_ranking_keyboard(current_view, chat_id):
    builder = InlineKeyboardBuilder()

    btn_season = InlineKeyboardButton(
        text=Messages.Ranking.BTN_TEMPORADA,
        callback_data=f"rank:temporada:{chat_id}",
        icon_custom_emoji_id=Emojis.ID_TEMPORADA,
        style="danger" if current_view == 'temporada' else None
    )
    btn_legacy = InlineKeyboardButton(
        text=Messages.Ranking.BTN_LEGADO,
        callback_data=f"rank:legado:{chat_id}",
        icon_custom_emoji_id=Emojis.ID_LEGADO,
        style="danger" if current_view == 'legado' else None
    )
    builder.add(btn_season, btn_legacy)

    btn_global = InlineKeyboardButton(
        text=Messages.Ranking.BTN_GLOBAL,
        callback_data=f"rank:global:{chat_id}",
        icon_custom_emoji_id=Emojis.ID_PLANETA,
        style="primary" if current_view == 'global' else None
    )
    builder.row(btn_global)

    builder.adjust(2, 1)
    return builder.as_markup()
