import random
from aiogram import types
from utils.messages import Messages


async def cmd_ping(message: types.Message):
    """/ping — healthcheck com resposta aleatória do cânone."""
    await message.reply(random.choice(Messages.System.PING_HEADERS), parse_mode="HTML")
