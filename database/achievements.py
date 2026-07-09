from datetime import datetime

from .pool import get_conn


async def register_achievement(user_id, chat_id, achievement_name):
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT 1 FROM achievements WHERE user_id = ? AND chat_id = ? AND achievement_name = ?',
            (user_id, chat_id, achievement_name))
        exists = await cursor.fetchone()
        if exists:
            return False
        await conn.execute(
            'INSERT INTO achievements (user_id, chat_id, achievement_name, unlocked_at) VALUES (?, ?, ?, ?)',
            (user_id, chat_id, achievement_name, int(datetime.now().timestamp())))
        await conn.commit()
        return True


async def get_achievements(user_id, chat_id):
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT achievement_name FROM achievements WHERE user_id = ? AND chat_id = ?',
            (user_id, chat_id))
        rows = await cursor.fetchall()
    return [r[0] for r in rows]


async def get_global_achievements(user_id):
    """Retorna todos os IDs únicos conquistadas em qualquer grupo."""
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT DISTINCT achievement_name FROM achievements WHERE user_id = ?',
            (user_id,))
        rows = await cursor.fetchall()
    return [row[0] for row in rows]


async def register_global_achievement(user_id, achievement_name):
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT 1 FROM global_achievements WHERE user_id = ? AND achievement_name = ?',
            (user_id, achievement_name))
        if await cursor.fetchone():
            return False
        await conn.execute(
            'INSERT INTO global_achievements (user_id, achievement_name, unlocked_at) VALUES (?, ?, ?)',
            (user_id, achievement_name, int(datetime.now().timestamp())))
        await conn.commit()
        return True


async def get_global_achievements_list(user_id):
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT achievement_name FROM global_achievements WHERE user_id = ?',
            (user_id,))
        rows = await cursor.fetchall()
    return [row[0] for row in rows]
