"""Helpers de detecção de contexto Telegram."""
from aiogram import types


async def is_group_chat(chat: types.Chat) -> bool:
    return chat.type in ('group', 'supergroup')
