from aiogram import types
from datetime import datetime, timedelta, timezone
from database import get_daily_winner, draw_daily_winner, increment_stat
from utils.messages import Messages
from utils.achievements_manager import check_achievements
from utils import is_group_chat, display_name
from config import GOD_MODE_GROUP_ID, DEV_GROUP_ID


async def cmd_bctdodia(message: types.Message):
    """/bctdodia — sorteia ou exibe a buceta do dia no grupo (1x/dia, pool: ativas nas últimas 72h)."""
    if not await is_group_chat(message.chat):
        return await message.reply(Messages.Errors.ONLY_GROUP, parse_mode='HTML')

    tz_sp = timezone(timedelta(hours=-3))
    now = datetime.now(tz_sp)
    date_str = now.strftime('%Y-%m-%d')
    chat_id = message.chat.id

    if chat_id in (GOD_MODE_GROUP_ID, DEV_GROUP_ID):
        # No laboratório, frauda o timestamp para burlar a trava de unicidade (date, chat_id) no banco.
        date_str = now.strftime('%Y-%m-%d %H:%M:%S.%f')

    winner = await get_daily_winner(chat_id, date_str)

    if not winner:
        winner = await draw_daily_winner(chat_id, date_str)

        if not winner:
            return await message.reply(Messages.BctDoDia.NO_ACTIVE_USERS, parse_mode='HTML')
        if winner.get("status") == "not_enough":
            return await message.reply(Messages.BctDoDia.NOT_ENOUGH_PLAYERS, parse_mode='HTML')

        winner_id = winner['user_id']
        await increment_stat(winner_id, chat_id, "bct_dia_wins")
        await check_achievements(winner_id, chat_id, "bct_dia", bot=message.bot)

        name = display_name(winner)
        is_self = message.from_user and message.from_user.id == winner_id
        return await message.reply(Messages.BctDoDia.get_winner_msg(name, winner['gain'], is_self=is_self), parse_mode='HTML')

    name = display_name(winner)
    is_self = message.from_user and message.from_user.id == winner['user_id']
    await message.reply(Messages.BctDoDia.get_status_msg(name, winner['gain'], is_self=is_self), parse_mode='HTML')
