"""
Pool de conexão aiosqlite com conexão persistente singleton.

aiosqlite não é thread-safe; serializamos escritas com asyncio.Lock.
SQLite em WAL permite leituras concorrentes, mas manter uma única
conexão evita overhead de open/close + PRAGMA por chamada.
"""
import asyncio
import logging
import aiosqlite
from contextlib import asynccontextmanager

DB_FILE = 'bot.db'


class _AsyncRLock:
    """Lock async re-entrante por task (permite get_conn() aninhado na mesma coroutine)."""

    def __init__(self):
        self._lock = asyncio.Lock()
        self._owner = None
        self._count = 0

    async def acquire(self):
        me = asyncio.current_task()
        if self._owner is me:
            self._count += 1
            return
        await self._lock.acquire()
        self._owner = me
        self._count = 1

    def release(self):
        self._count -= 1
        if self._count == 0:
            self._owner = None
            self._lock.release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, *_):
        self.release()


_db: aiosqlite.Connection | None = None
_lock: _AsyncRLock | None = None


async def init_pool():
    """Inicializa a conexão singleton + PRAGMAs. Chamar uma vez no startup."""
    global _db, _lock
    if _db is not None:
        return
    _lock = _AsyncRLock()
    _db = await aiosqlite.connect(DB_FILE, timeout=30)
    await _db.execute("PRAGMA journal_mode=WAL")
    await _db.execute("PRAGMA synchronous=NORMAL")
    await _db.execute("PRAGMA foreign_keys=ON")
    await _db.commit()
    logging.info("DB pool inicializado (single persistent connection, WAL).")


async def close_pool():
    global _db
    if _db is not None:
        await _db.close()
        _db = None


@asynccontextmanager
async def get_conn():
    """
    Contexto de acesso à conexão singleton.
    Serializa acesso com lock para respeitar a não-thread-safety do aiosqlite.
    """
    if _db is None:
        # Fallback para scripts one-shot que esquecem de chamar init_pool()
        await init_pool()
    async with _lock:
        yield _db


async def ensure_column(conn, table_name, column_name, column_definition):
    cursor = await conn.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in await cursor.fetchall()]
    if column_name not in columns:
        logging.info(f"Blindagem: Adicionando coluna '{column_name}' na tabela '{table_name}'...")
        try:
            await conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
        except aiosqlite.OperationalError as e:
            logging.error(f"Erro ao adicionar coluna {column_name}: {e}")
