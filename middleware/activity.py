"""
Rastreia atividade (last_seen) e mantém lista de grupos atualizada
para o sorteio do /bctdodia.

Debounce TTL de 300s (5min) reduz writes em grupos grandes.
Update roda em background (asyncio.create_task) — handler libera
imediato sem esperar IO no DB.
"""
import asyncio
import logging
import time
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.enums import ChatType
from database import update_activity, upsert_group

_TTL_SECONDS = 300
_last_write: dict[tuple[int, int], float] = {}
_background_tasks: set[asyncio.Task] = set()


async def _do_update(chat_id: int, chat_title, chat_username,
                     user_id: int, username, first_name, last_name) -> None:
    try:
        await upsert_group(chat_id, chat_title, chat_username)
        await update_activity(user_id, chat_id,
                              username=username,
                              first_name=first_name,
                              last_name=last_name)
    except Exception as e:
        logging.debug(f"ActivityMiddleware update falhou: {e}")


class ActivityMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        if getattr(event, "from_user", None) is None or event.from_user.is_bot:
            return await handler(event, data)

        if event.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            key = (event.from_user.id, event.chat.id)
            now = time.time()
            last = _last_write.get(key, 0.0)

            if now - last >= _TTL_SECONDS:
                _last_write[key] = now
                username = f"@{event.from_user.username}" if event.from_user.username else None
                task = asyncio.create_task(_do_update(
                    event.chat.id, event.chat.title, event.chat.username,
                    event.from_user.id, username,
                    event.from_user.first_name, event.from_user.last_name,
                ))
                _background_tasks.add(task)
                task.add_done_callback(_background_tasks.discard)

        return await handler(event, data)
