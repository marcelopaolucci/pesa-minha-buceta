from .pool import get_conn


async def save_duel(message_id, challenger_id, challenger_name, chat_id, stake, timestamp):
    async with get_conn() as conn:
        await conn.execute('''
            INSERT INTO open_duels (message_id, challenger_id, challenger_name, chat_id, stake, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (message_id, challenger_id, challenger_name, chat_id, stake, timestamp))
        await conn.commit()


async def get_duel(message_id):
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT challenger_id, challenger_name, chat_id, stake, timestamp FROM open_duels WHERE message_id = ?',
            (message_id,))
        row = await cursor.fetchone()
    if row:
        return {
            "challenger_id": row[0],
            "challenger_name": row[1],
            "chat_id": row[2],
            "stake": row[3],
            "timestamp": row[4]
        }
    return None


async def delete_duel(message_id):
    async with get_conn() as conn:
        await conn.execute('DELETE FROM open_duels WHERE message_id = ?', (message_id,))
        await conn.commit()


async def get_duel_cooldown(user_id, chat_id):
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT last_duel FROM duel_cooldowns WHERE user_id = ? AND chat_id = ?',
            (user_id, chat_id))
        row = await cursor.fetchone()
    return row[0] if row else None


async def set_duel_cooldown(user_id, chat_id, timestamp):
    async with get_conn() as conn:
        await conn.execute('''
            INSERT INTO duel_cooldowns (user_id, chat_id, last_duel)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, chat_id) DO UPDATE SET last_duel = excluded.last_duel
        ''', (user_id, chat_id, timestamp))
        await conn.commit()


async def transfer_duel_weight(winner_id, loser_id, chat_id, stake):
    async with get_conn() as conn:
        await conn.execute("BEGIN")
        await conn.execute(
            "UPDATE users SET peso_legado = peso_legado + ? WHERE user_id = ? AND chat_id = ?",
            (stake, winner_id, chat_id))
        await conn.execute(
            "UPDATE users SET peso_legado = peso_legado - ? WHERE user_id = ? AND chat_id = ?",
            (stake, loser_id, chat_id))
        await conn.commit()
