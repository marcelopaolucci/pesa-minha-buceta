from .pool import get_conn

_VALID_STAT_COLUMNS = frozenset({"duels_won", "duels_lost", "kg_donated", "donations_made", "bct_dia_wins", "total_weighs"})

EMPTY_STATS = {
    "duels_won": 0, "duels_lost": 0, "kg_donated": 0,
    "donations_made": 0, "bct_dia_wins": 0, "total_weighs": 0,
}


async def _ensure_stats_row(conn, user_id, chat_id):
    """Garante que o usuário tenha uma linha na tabela user_stats."""
    cursor = await conn.execute('SELECT 1 FROM user_stats WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
    if not await cursor.fetchone():
        await conn.execute('INSERT INTO user_stats (user_id, chat_id) VALUES (?, ?)', (user_id, chat_id))


async def increment_stat(user_id, chat_id, column, increment=1):
    """Incrementa uma estatística específica de um usuário."""
    if column not in _VALID_STAT_COLUMNS:
        raise ValueError(f"Invalid stat column: {column!r}")
    async with get_conn() as conn:
        await _ensure_stats_row(conn, user_id, chat_id)
        await conn.execute(f'UPDATE user_stats SET {column} = {column} + ? WHERE user_id = ? AND chat_id = ?',
                           (increment, user_id, chat_id))
        await conn.commit()


async def get_user_stats(user_id, chat_id):
    """Retorna todas as estatísticas de um usuário em um grupo específico."""
    async with get_conn() as conn:
        await _ensure_stats_row(conn, user_id, chat_id)
        cursor = await conn.execute('''
            SELECT duels_won, duels_lost, kg_donated, donations_made, bct_dia_wins, total_weighs
            FROM user_stats WHERE user_id = ? AND chat_id = ?
        ''', (user_id, chat_id))
        row = await cursor.fetchone()
        await conn.commit()
    if row:
        return {
            "duels_won": row[0],
            "duels_lost": row[1],
            "kg_donated": row[2],
            "donations_made": row[3],
            "bct_dia_wins": row[4],
            "total_weighs": row[5]
        }
    return dict(EMPTY_STATS)


async def get_global_user_stats(user_id):
    """Soma todas as estatísticas do usuário em todos os grupos onde ele já atuou."""
    async with get_conn() as conn:
        cursor = await conn.execute('''
            SELECT SUM(duels_won), SUM(duels_lost), SUM(kg_donated), SUM(donations_made), SUM(bct_dia_wins), SUM(total_weighs)
            FROM user_stats WHERE user_id = ?
        ''', (user_id,))
        row = await cursor.fetchone()

    if row and row[0] is not None:
        return {
            "duels_won": row[0],
            "duels_lost": row[1],
            "kg_donated": row[2],
            "donations_made": row[3],
            "bct_dia_wins": row[4],
            "total_weighs": row[5] or 0
        }
    return dict(EMPTY_STATS)


async def get_global_peso_legado_total(user_id):
    """Consolida o peso legado de todos os grupos locais."""
    async with get_conn() as conn:
        cursor = await conn.execute('SELECT SUM(peso_legado) FROM users WHERE user_id = ?', (user_id,))
        total = (await cursor.fetchone())[0] or 0.0
    return total


async def get_global_legado_historico(user_id):
    """Legado global unificado = soma do peso_legado do usuário em todos os grupos
    locais (tua massa total no Telegram). O antigo legado global (global_users +
    global_seasons_history) foi aposentado na unificação global↔local."""
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT SUM(peso_legado) FROM users WHERE user_id = ?', (user_id,)
        )
        total = (await cursor.fetchone())[0] or 0.0
    return total


async def get_total_weighs_from_history(user_id) -> int:
    """Conta todas as pesagens do usuário em weight_history (local + global, toda a história)."""
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT COUNT(*) FROM weight_history WHERE user_id = ?', (user_id,)
        )
        row = await cursor.fetchone()
    return row[0] if row else 0


async def get_local_weighs_count(user_id, chat_id) -> int:
    """Conta pesagens do usuário num grupo específico."""
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT COUNT(*) FROM weight_history WHERE user_id = ? AND chat_id = ?', (user_id, chat_id)
        )
        row = await cursor.fetchone()
    return row[0] if row else 0


async def get_total_local_legado_sum(user_id) -> float:
    """Soma peso_legado do usuário em todos os grupos locais."""
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT SUM(peso_legado) FROM users WHERE user_id = ?', (user_id,)
        )
        row = await cursor.fetchone()
    return row[0] or 0.0 if row else 0.0


async def get_groups_count(user_id):
    """Conta em quantos chats diferentes o usuário já pesou."""
    async with get_conn() as conn:
        cursor = await conn.execute('SELECT COUNT(DISTINCT chat_id) FROM users WHERE user_id = ?', (user_id,))
        count_row = await cursor.fetchone()
    return count_row[0] if count_row else 0


async def get_total_system_data():
    """Retorna estatísticas consolidadas de todo o ecossistema do bot."""
    async with get_conn() as conn:
        cursor = await conn.execute('SELECT COUNT(DISTINCT user_id) FROM users')
        total_users = (await cursor.fetchone())[0] or 0

        cursor = await conn.execute('SELECT COUNT(*) FROM groups')
        total_groups = (await cursor.fetchone())[0] or 0

        cursor = await conn.execute('SELECT SUM(peso_legado) FROM users')
        total_weight_grams = (await cursor.fetchone())[0] or 0.0
        total_kg = total_weight_grams / 1000.0

    return {
        "total_users": total_users,
        "total_groups": total_groups,
        "total_kg": total_kg
    }
