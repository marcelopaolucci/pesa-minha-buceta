"""Cache singleton do Bot.me (username/id) — nunca muda em runtime."""
from aiogram import Bot
from aiogram.types import User

_bot_me: User | None = None


async def get_bot_me(bot: Bot) -> User:
    """Retorna o User do bot, cacheando após primeira chamada."""
    global _bot_me
    if _bot_me is None:
        _bot_me = await bot.get_me()
    return _bot_me
