from aiogram import types
from aiogram.filters import CommandObject
from utils.messages import Messages
from utils.keyboards import get_help_markup
from utils import safe_edit
from services.bot_cache import get_bot_me

# Mapeamento estático de páginas de ajuda — construído uma vez, reutilizado em todos os callbacks.
_HELP_PAGES = {
    "main":         Messages.Help.MAIN,
    "pesar_local":  Messages.Help.PESAR_LOCAL,
    "pesar_global": Messages.Help.PESAR_GLOBAL,
    "reset":        Messages.Help.RESET,
    "ranking":      Messages.Help.RANKING,
    "duelo":        Messages.Help.DUELO,
    "doar":         Messages.Help.DOAR,
    "conquistas":   Messages.Help.CONQUISTAS,
    "perfil":       Messages.Help.PERFIL,
    "bctdodia":     Messages.Help.BCTDODIA,
}


async def cmd_ajuda(message: types.Message):
    """/ajuda — envia o manual principal."""
    await _send_help(message)


async def cmd_start(message: types.Message, command: CommandObject):
    """/start — alias de /ajuda. Deep link ?start=conquistas abre o Grimório."""
    if command.args == "conquistas":
        from handlers.conquistas import show_conquistas_logic
        await show_conquistas_logic(message, user_override=message.from_user, view_mode='personal')
        return
    await _send_help(message)


async def welcome_new_chat(message: types.Message):
    """Dispara quando o bot é adicionado a um grupo."""
    if not message.new_chat_members:
        return
    bot_me = await get_bot_me(message.bot)
    for member in message.new_chat_members:
        if member.id == bot_me.id:
            await _send_help(message)
            break


async def _send_help(message: types.Message):
    """Envia o manual principal."""
    bot_user = await get_bot_me(message.bot)
    markup = get_help_markup("main", bot_user.username)
    await message.reply(Messages.Help.MAIN, parse_mode='HTML', reply_markup=markup)


async def process_help_callback(query: types.CallbackQuery):
    """Navega entre páginas do manual via inline buttons."""
    parts = query.data.split(":")
    if len(parts) < 2:
        await query.answer()
        return

    action = parts[1]
    text = _HELP_PAGES.get(action) or _HELP_PAGES["main"]

    bot_user = await get_bot_me(query.bot)
    markup = get_help_markup(action, bot_user.username)

    await safe_edit(query, text, reply_markup=markup)
    await query.answer()
