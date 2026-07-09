from datetime import datetime

from .pool import get_conn
from .seasons import get_current_season
from config import ALLOWED_USER_ID, GOD_MODE_GROUP_ID, DEV_GROUP_ID


async def update_user(user_id, username, first_name, last_name, chat_id, weight_change=None):
    async with get_conn() as conn:
        cursor = await conn.execute('SELECT peso_legado, peso_temporada FROM users WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        user = await cursor.fetchone()
        current_date = datetime.now().strftime('%Y-%m-%d')
        if user is None:
            new_weight = 0.0 if weight_change is None else weight_change
            await conn.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, chat_id, peso_legado, peso_temporada, last_update)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, chat_id, new_weight, new_weight, current_date))
        else:
            if weight_change is not None:
                new_legado = user[0] + weight_change
                new_temporada = user[1] + weight_change
                await conn.execute('''
                    UPDATE users SET peso_legado = ?, peso_temporada = ?, last_update = ?, username = ?, first_name = ?, last_name = ?, last_seen = ?
                    WHERE user_id = ? AND chat_id = ?
                ''', (new_legado, new_temporada, current_date, username, first_name, last_name, int(datetime.now().timestamp()), user_id, chat_id))
            else:
                await conn.execute('''
                    UPDATE users SET last_seen = ?
                    WHERE user_id = ? AND chat_id = ?
                ''', (int(datetime.now().timestamp()), user_id, chat_id))
        await conn.commit()


async def update_activity(user_id, chat_id, username=None, first_name=None, last_name=None):
    """Atualiza apenas o timestamp de última atividade."""
    async with get_conn() as conn:
        now_ts = int(datetime.now().timestamp())
        cursor = await conn.execute('''
            UPDATE users
            SET last_seen = ?,
                username = COALESCE(?, username),
                first_name = COALESCE(?, first_name),
                last_name = COALESCE(?, last_name)
            WHERE user_id = ? AND chat_id = ?
        ''', (now_ts, username, first_name, last_name, user_id, chat_id))
        if cursor.rowcount == 0 and first_name:
            await conn.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, chat_id, peso_legado, peso_temporada, last_update, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, chat_id, 0.0, 0.0, "2000-01-01", now_ts))
        await conn.commit()


async def get_user_name(user_id, chat_id):
    """Retorna o nome formatado do usuário (First Name ou Username)."""
    async with get_conn() as conn:
        cursor = await conn.execute('SELECT first_name, username FROM users WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        row = await cursor.fetchone()
    if row:
        return row[0] or row[1] or "Alguém"
    return "Alguém"


async def can_update(user_id, chat_id):
    if user_id == ALLOWED_USER_ID and (chat_id == GOD_MODE_GROUP_ID or chat_id == DEV_GROUP_ID):
        return True
    async with get_conn() as conn:
        cursor = await conn.execute('SELECT last_update FROM users WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        user = await cursor.fetchone()
    if user is None or user[0] is None:
        return True
    last_update_str = user[0]
    today_str = datetime.now().strftime('%Y-%m-%d')
    return last_update_str != today_str


async def get_peso_legado(user_id, chat_id):
    async with get_conn() as conn:
        cursor = await conn.execute('SELECT peso_legado FROM users WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        user = await cursor.fetchone()
    return user[0] if user else 0.0


async def get_peso_legado_or_none(user_id, chat_id):
    """Igual get_peso_legado, mas retorna None se usuário não existe (vs 0.0)."""
    async with get_conn() as conn:
        cursor = await conn.execute('SELECT peso_legado FROM users WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        user = await cursor.fetchone()
    return user[0] if user else None


async def get_peso_temporada(user_id, chat_id):
    async with get_conn() as conn:
        cursor = await conn.execute('SELECT peso_temporada FROM users WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        user = await cursor.fetchone()
    return user[0] if user else 0.0


async def get_global_weight(user_id):
    """Peso global (temporada) unificado = MAX(peso_temporada) do usuário entre os
    grupos JÁ na temporada atual (grupo não-resetado tem temporada stale — excluído).
    Mesmo pico que rankeia no ranking global derivado."""
    async with get_conn() as conn:
        cursor = await conn.execute('''
            SELECT MAX(u.peso_temporada) FROM users u
            JOIN groups g ON u.chat_id = g.chat_id
            WHERE u.user_id = ? AND g.last_season_id = ?
        ''', (user_id, get_current_season()))
        row = await cursor.fetchone()
    return (row[0] or 0.0) if row else 0.0


async def get_local_rank(user_id, chat_id, column="peso_temporada"):
    col = "peso_legado" if column == "peso_legado" else "peso_temporada"
    async with get_conn() as conn:
        cursor = await conn.execute(f'''
            SELECT
                u.{col} AS w,
                (SELECT COUNT(*) FROM users WHERE chat_id = ? AND {col} > u.{col} AND user_id != ?) AS higher
            FROM users u
            WHERE u.user_id = ? AND u.chat_id = ?
        ''', (chat_id, ALLOWED_USER_ID, user_id, chat_id))
        row = await cursor.fetchone()
    if not row or row[0] == 0.0:
        return "?"
    return row[1] + 1


async def get_global_legado_rank(user_id):
    """Rank global de legado unificado = posição por SUM(peso_legado) do usuário
    entre todos os grupos (tua massa total no Telegram)."""
    async with get_conn() as conn:
        cursor = await conn.execute('SELECT SUM(peso_legado) FROM users WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        my_legado = (row[0] or 0.0) if row else 0.0
        if my_legado == 0.0:
            return "?"
        cursor = await conn.execute('''
            SELECT COUNT(*) FROM (
                SELECT user_id, SUM(peso_legado) AS total FROM users
                WHERE user_id != ?
                GROUP BY user_id
                HAVING total > ?
            )
        ''', (ALLOWED_USER_ID, my_legado))
        row = await cursor.fetchone()
    return (row[0] or 0) + 1


async def get_global_rank(user_id):
    """Rank global (temporada) unificado = posição no leaderboard derivado de
    MAX(peso_temporada), contando só grupos JÁ na temporada atual (stale excluído).
    Mesmo critério do ranking global."""
    season = get_current_season()
    async with get_conn() as conn:
        cursor = await conn.execute('''
            SELECT MAX(u.peso_temporada) FROM users u
            JOIN groups g ON u.chat_id = g.chat_id
            WHERE u.user_id = ? AND g.last_season_id = ?
        ''', (user_id, season))
        row = await cursor.fetchone()
        my_max = (row[0] or 0.0) if row else 0.0
        if my_max == 0.0:
            return "?"
        cursor = await conn.execute('''
            SELECT COUNT(*) FROM (
                SELECT u.user_id, MAX(u.peso_temporada) AS m FROM users u
                JOIN groups g ON u.chat_id = g.chat_id
                WHERE u.user_id != ? AND g.last_season_id = ?
                GROUP BY u.user_id
                HAVING m > ?
            )
        ''', (ALLOWED_USER_ID, season, my_max))
        row = await cursor.fetchone()
    return (row[0] or 0) + 1


async def transfer_donation(donor_id, receiver_id, chat_id, amount_grams):
    """
    Transfere peso_legado do doador para o recebedor atomicamente.

    Retorna dict:
      {"status": "donor_not_weighed"}            doador nunca pesou
      {"status": "insufficient", "balance": g}   doador sem saldo (em gramas)
      {"status": "receiver_not_weighed"}         recebedor nunca pesou
      {"status": "ok", "receiver_weight_before": g}
    """
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT peso_legado FROM users WHERE user_id = ? AND chat_id = ?',
            (donor_id, chat_id))
        donor_row = await cursor.fetchone()
        if not donor_row:
            return {"status": "donor_not_weighed"}
        if donor_row[0] < amount_grams:
            return {"status": "insufficient", "balance": donor_row[0]}

        cursor = await conn.execute(
            'SELECT peso_legado FROM users WHERE user_id = ? AND chat_id = ?',
            (receiver_id, chat_id))
        receiver_row = await cursor.fetchone()
        if not receiver_row:
            return {"status": "receiver_not_weighed"}

        receiver_weight_before = receiver_row[0]

        cursor = await conn.execute(
            'UPDATE users SET peso_legado = peso_legado - ? WHERE user_id = ? AND chat_id = ? AND peso_legado >= ?',
            (amount_grams, donor_id, chat_id, amount_grams))
        if cursor.rowcount == 0:
            return {"status": "insufficient", "balance": donor_row[0]}

        await conn.execute(
            'UPDATE users SET peso_legado = peso_legado + ? WHERE user_id = ? AND chat_id = ?',
            (amount_grams, receiver_id, chat_id))
        await conn.commit()
        return {"status": "ok", "receiver_weight_before": receiver_weight_before}


async def inject_weight(user_id, chat_id, amount_grams, display_name):
    """Admin cheat: soma amount_grams ao peso_legado (cria usuário se ausente)."""
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT peso_legado FROM users WHERE user_id = ? AND chat_id = ?',
            (user_id, chat_id))
        row = await cursor.fetchone()
        if not row:
            await conn.execute('''
                INSERT INTO users (user_id, chat_id, username, first_name, last_name,
                                   peso_legado, peso_temporada, last_update)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, chat_id, "admin_cheat", display_name, "",
                  amount_grams, 0, "2000-01-01"))
        else:
            await conn.execute(
                'UPDATE users SET peso_legado = peso_legado + ? WHERE user_id = ? AND chat_id = ?',
                (amount_grams, user_id, chat_id))
        await conn.commit()


async def reset_user(user_id, chat_id):
    async with get_conn() as conn:
        await conn.execute('DELETE FROM users WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        await conn.execute('DELETE FROM weight_history WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        await conn.execute('DELETE FROM interactions WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        await conn.execute('DELETE FROM achievements WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        await conn.execute('DELETE FROM user_stats WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        await conn.execute('DELETE FROM user_group_meta WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        await conn.commit()


async def get_user_groups(user_id):
    """Retorna lista de (chat_id, title) dos grupos onde o usuário está registrado."""
    async with get_conn() as conn:
        cursor = await conn.execute('''
            SELECT DISTINCT u.chat_id, g.title
            FROM users u
            LEFT JOIN groups g ON u.chat_id = g.chat_id
            WHERE u.user_id = ?
        ''', (user_id,))
        return await cursor.fetchall()


async def get_user_meta(user_id, chat_id):
    """Retorna os metadados do usuário específicos daquele CHAT_ID: pity_counter, streak_count e max_streak."""
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT pity_counter, streak_count, last_streak_date, max_streak_count FROM user_group_meta WHERE user_id = ? AND chat_id = ?',
            (user_id, chat_id))
        row = await cursor.fetchone()

    if not row:
        return {"pity": 0, "streak": 0, "last_date": None, "max_streak": 0}
    return {"pity": row[0], "streak": row[1], "last_date": row[2], "max_streak": row[3]}
