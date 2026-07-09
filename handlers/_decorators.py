"""Decorators reutilizáveis para handlers."""
from functools import wraps
from typing import Optional, Callable
from aiogram.types import Message
from config import ALLOWED_USER_ID


def owner_only(*, silent: bool = True, deny_msg: Optional[str] = None) -> Callable:
    """
    Bloqueia handler se from_user não é o dono do bot.

    Args:
        silent: se True (default), ignora silenciosamente.
                Se False, responde a mensagem com `deny_msg` antes de retornar.
        deny_msg: HTML a enviar quando silent=False.

    Uso:
        @owner_only()
        async def cmd_anunciar(message): ...

        @owner_only(silent=False, deny_msg=Messages.Errors.INJETAR_DENIED)
        async def cmd_injetar(message, command=None): ...
    """
    def deco(fn):
        @wraps(fn)
        async def wrapper(message: Message, *args, **kwargs):
            if not message.from_user or message.from_user.id != ALLOWED_USER_ID:
                if not silent and deny_msg:
                    await message.reply(deny_msg, parse_mode='HTML')
                return
            return await fn(message, *args, **kwargs)
        return wrapper
    return deco
