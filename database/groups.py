import logging

from .pool import get_conn
from .seasons import get_current_season


async def get_all_groups():
    """Retorna a lista de (chat_id, title) de todos os grupos registrados."""
    async with get_conn() as conn:
        cursor = await conn.execute('SELECT chat_id, title FROM groups')
        return await cursor.fetchall()


async def delete_group(chat_id):
    """Remove o grupo e todos os usuários vinculados a ele (limpeza automática)."""
    async with get_conn() as conn:
        try:
            logging.info(f"Limpeza Automática: Removendo grupo {chat_id} e seus usuários...")
            await conn.execute('DELETE FROM groups WHERE chat_id = ?', (chat_id,))
            await conn.execute('DELETE FROM users WHERE chat_id = ?', (chat_id,))
            await conn.execute('DELETE FROM user_group_meta WHERE chat_id = ?', (chat_id,))
            await conn.execute('DELETE FROM achievements WHERE chat_id = ?', (chat_id,))
            await conn.execute('DELETE FROM user_stats WHERE chat_id = ?', (chat_id,))
            await conn.commit()
        except Exception as e:
            logging.error(f"Erro ao deletar grupo {chat_id}: {e}")
            await conn.rollback()


async def upsert_group(chat_id, title, username):
    async with get_conn() as conn:
        current_season = get_current_season()
        await conn.execute('''
            INSERT INTO groups (chat_id, title, username, last_season_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                title = excluded.title,
                username = excluded.username
        ''', (chat_id, title, username, current_season))
        await conn.commit()
