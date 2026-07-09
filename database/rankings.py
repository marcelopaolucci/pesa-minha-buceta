from .pool import get_conn
from .seasons import get_current_season
from config import ALLOWED_USER_ID


async def get_leaderboard(chat_id, limit=20, column="peso_temporada"):
    async with get_conn() as conn:
        if chat_id == 0:
            # Global unificado: derivado do peso_temporada local. Peso global de cada
            # usuário = MAX(peso_temporada) entre todos os grupos dele (a maior buceta
            # de qualquer grupo é a maior buceta do Telegram). GROUP BY user_id deduplica
            # — cada um aparece 1x, pelo seu pico. SQLite popula as bare columns
            # (username/first_name/last_name) a partir da linha do MAX().
            # Só grupos JÁ na temporada atual (last_season_id = current) contam: grupo
            # não-resetado ainda carrega peso_temporada da season passada (stale) — o
            # reset é lazy, então filtrar aqui garante que o global reflita só o T atual.
            # Legado global foi eliminado na unificação — não há ranking legado global.
            if column == "peso_legado":
                return []
            cursor = await conn.execute('''
                SELECT u.username, u.first_name, u.last_name, MAX(u.peso_temporada) AS w
                FROM users u
                JOIN groups g ON u.chat_id = g.chat_id
                WHERE u.peso_temporada > 0 AND u.user_id != ?
                  AND g.last_season_id = ?
                GROUP BY u.user_id
                ORDER BY w DESC LIMIT ?
            ''', (ALLOWED_USER_ID, get_current_season(), limit))
        else:
            col = "peso_legado" if column == "peso_legado" else "peso_temporada"
            cursor = await conn.execute(f'''
                SELECT username, first_name, last_name, {col}
                FROM users WHERE chat_id = ? AND user_id != ? ORDER BY {col} DESC LIMIT ?
            ''', (chat_id, ALLOWED_USER_ID, limit))
        return await cursor.fetchall()


async def get_weekly_ranking(chat_id):
    async with get_conn() as conn:
        cursor = await conn.execute('''
            SELECT u.username, u.first_name, u.last_name, SUM(h.weight_change) as total_gain
            FROM weight_history h
            JOIN users u ON h.user_id = u.user_id AND h.chat_id = u.chat_id
            WHERE h.chat_id = ? AND h.user_id != ? AND h.timestamp >= (strftime('%s', 'now') - 604800)
            GROUP BY h.user_id
            ORDER BY total_gain DESC
            LIMIT 20
        ''', (chat_id, ALLOWED_USER_ID))
        return await cursor.fetchall()


async def get_monthly_ranking(chat_id):
    async with get_conn() as conn:
        cursor = await conn.execute('''
            SELECT u.username, u.first_name, u.last_name, SUM(h.weight_change) as total_gain
            FROM weight_history h
            JOIN users u ON h.user_id = u.user_id AND h.chat_id = u.chat_id
            WHERE h.chat_id = ? AND h.user_id != ? AND h.timestamp >= (strftime('%s', 'now') - 2592000)
            GROUP BY h.user_id
            ORDER BY total_gain DESC
            LIMIT 20
        ''', (chat_id, ALLOWED_USER_ID))
        return await cursor.fetchall()
