import random
import re
from aiogram import Router, F
from aiogram.types import Message, ReactionTypeEmoji
from utils import is_group_chat

router = Router()

_RE_BCT = re.compile(r'\b(bucetas?|bucetão|bucetinha|bct)\b')


@router.message(F.text)
async def handle_keywords(message: Message):
    """Reage com 🔥 a mensagens contendo variações de 'buceta' (30% de chance)."""
    if message.text.startswith('/'):
        return

    if not await is_group_chat(message.chat):
        return

    if _RE_BCT.search(message.text.lower()) and random.random() < 0.3:
        try:
            await message.bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[ReactionTypeEmoji(emoji="🔥")]
            )
        except Exception:
            pass
