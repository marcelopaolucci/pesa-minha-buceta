import logging
from datetime import datetime

from .pool import get_conn


def get_current_season():
    """Calcula a temporada atual baseada no trimestre civil."""
    now = datetime.now()
    year = now.year
    month = now.month
    # Ex: 2026 Q1=S1, Q2=S2 (Abril/Maio/Junho)
    return (year - 2026) * 4 + ((month - 1) // 3) + 1


def get_season_label(season_id):
    """Retorna o rótulo amigável da temporada (ex: T2 - 2026)."""
    base_year = 2026
    offset = season_id - 1
    year = base_year + (offset // 4)
    q = (offset % 4) + 1
    return f"T{q} — {year}"


async def _archive_previous_season(conn, current_season):
    """Arquivamento Silencioso (Auto-Wipe) das 10 Maiores de temporadas passadas."""
    prev_season = current_season - 1
    if prev_season < 1:
        return

    cursor = await conn.execute("SELECT value FROM bot_metadata WHERE key = 'last_archived_season'")
    res = await cursor.fetchone()
    last_archived = int(res[0]) if res else 0

    if last_archived < prev_season:
        cursor = await conn.execute('''
            SELECT user_id, weight, (first_name || ' ' || last_name) as name, username
            FROM global_users WHERE season_id = ? ORDER BY weight DESC LIMIT 20
        ''', (prev_season,))
        top_players = await cursor.fetchall()

        for i, (uid, w, name, uname) in enumerate(top_players, 1):
            display_name = name or uname or "Anônima"
            await conn.execute('''
                INSERT OR REPLACE INTO global_seasons_history (season_id, user_id, weight, rank, name_cache)
                VALUES (?, ?, ?, ?, ?)
            ''', (prev_season, uid, w, i, display_name))

        await conn.execute("UPDATE bot_metadata SET value = ? WHERE key = 'last_archived_season'", (prev_season,))
        logging.info(f"Temporada {prev_season} arquivada com sucesso.")


async def finalize_local_season(chat_id, override_season_id=None):
    """
    Finaliza a temporada atual de um grupo:
    1. Salva o Top 20 no Hall da Fama Local.
    2. Reseta o peso_temporada de todos os usuários do grupo.
    3. Retorna os nomes dos vencedores para feedback.
    """
    async with get_conn() as conn:
        try:
            season_id = override_season_id or get_current_season()

            cursor = await conn.execute('''
                SELECT user_id, first_name, username, peso_temporada
                FROM users
                WHERE chat_id = ? AND peso_temporada > 0
                ORDER BY peso_temporada DESC LIMIT 20
            ''', (chat_id,))
            winners = await cursor.fetchall()

            results = []
            for i, (u_id, f_name, u_name, weight) in enumerate(winners, 1):
                name = f_name or u_name or "Anônima"
                results.append({"name": name, "weight": weight, "rank": i})

                await conn.execute('''
                    INSERT OR REPLACE INTO hall_da_fama_local
                    (season_id, chat_id, user_id, peso_temporada_final, rank, name_cache)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (season_id, chat_id, u_id, weight, i, name))

            await conn.execute('UPDATE users SET peso_temporada = 0 WHERE chat_id = ?', (chat_id,))

            current_season = get_current_season()
            await conn.execute('UPDATE groups SET last_season_id = ? WHERE chat_id = ?', (current_season, chat_id))

            await conn.commit()
            return results
        except Exception as e:
            logging.error(f"Erro ao finalizar temporada local no chat {chat_id}: {e}")
            await conn.rollback()
            return None


async def get_hall_of_fame(season_id):
    """Retorna as lendas de uma temporada específica."""
    async with get_conn() as conn:
        cursor = await conn.execute('''
            SELECT name_cache, weight
            FROM global_seasons_history WHERE season_id = ? ORDER BY weight DESC
        ''', (season_id,))
        return await cursor.fetchall()


async def get_available_seasons():
    """Retorna lista de temporadas que possuem Hall da Fama."""
    async with get_conn() as conn:
        cursor = await conn.execute('SELECT DISTINCT season_id FROM global_seasons_history ORDER BY season_id DESC')
        rows = await cursor.fetchall()
        return [r[0] for r in rows]


async def get_hall_of_fame_local(chat_id, season_id):
    """Retorna o Hall da Fama local de um grupo/temporada."""
    async with get_conn() as conn:
        cursor = await conn.execute('''
            SELECT name_cache, peso_temporada_final, rank
            FROM hall_da_fama_local
            WHERE chat_id = ? AND season_id = ?
            ORDER BY rank ASC
        ''', (chat_id, season_id))
        return await cursor.fetchall()
