import logging

from .pool import get_conn, ensure_column


async def init_db():
    async with get_conn() as conn:
        # 1. Tabelas Base
        await conn.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            chat_id INTEGER,
            peso_legado REAL DEFAULT 0,
            peso_temporada REAL DEFAULT 0,
            last_update TEXT,
            last_seen INTEGER,
            PRIMARY KEY (user_id, chat_id)
        )''')

        # 2. Blindagem de Migração: Users
        cursor = await conn.execute("PRAGMA table_info(users)")
        user_columns = [col[1] for col in await cursor.fetchall()]
        if 'weight' in user_columns and 'peso_legado' not in user_columns:
            logging.info("Migrando coluna 'weight' para 'peso_legado'...")
            await conn.execute("ALTER TABLE users RENAME COLUMN weight TO peso_legado")

        await ensure_column(conn, "users", "peso_temporada", "REAL DEFAULT 0")
        await ensure_column(conn, "users", "last_seen", "INTEGER")

        await conn.execute('''CREATE TABLE IF NOT EXISTS groups (
            chat_id INTEGER PRIMARY KEY,
            title TEXT,
            username TEXT,
            last_season_id INTEGER DEFAULT 1
        )''')

        await ensure_column(conn, "groups", "last_season_id", "INTEGER DEFAULT 1")

        await conn.execute('''CREATE TABLE IF NOT EXISTS user_group_meta (
            user_id INTEGER,
            chat_id INTEGER,
            pity_counter INTEGER DEFAULT 0,
            streak_count INTEGER DEFAULT 1,
            last_streak_date TEXT,
            max_streak_count INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, chat_id)
        )''')

        await ensure_column(conn, "user_group_meta", "max_streak_count", "INTEGER DEFAULT 0")

        # 3. Restante das Tabelas Estruturais
        await conn.execute('''CREATE TABLE IF NOT EXISTS daily_winners (
            date TEXT, chat_id INTEGER, user_id INTEGER, weight_gain REAL,
            PRIMARY KEY (date, chat_id)
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS weight_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, chat_id INTEGER,
            weight_change REAL, timestamp INTEGER
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS interactions (
            user_id INTEGER, chat_id INTEGER, count INTEGER, PRIMARY KEY (user_id, chat_id)
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS achievements (
            user_id INTEGER, chat_id INTEGER, achievement_name TEXT, unlocked_at INTEGER,
            PRIMARY KEY (user_id, chat_id, achievement_name)
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS global_achievements (
            user_id INTEGER, achievement_name TEXT, unlocked_at INTEGER,
            PRIMARY KEY (user_id, achievement_name)
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS open_duels (
            message_id INTEGER PRIMARY KEY, challenger_id INTEGER, challenger_name TEXT,
            chat_id INTEGER, stake REAL, timestamp INTEGER
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER, chat_id INTEGER, duels_won INTEGER DEFAULT 0,
            duels_lost INTEGER DEFAULT 0, kg_donated REAL DEFAULT 0,
            donations_made INTEGER DEFAULT 0, bct_dia_wins INTEGER DEFAULT 0,
            total_weighs INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, chat_id)
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS global_users (
            user_id INTEGER, season_id INTEGER, weight REAL DEFAULT 0,
            last_update TEXT, username TEXT, first_name TEXT, last_name TEXT,
            PRIMARY KEY (user_id, season_id)
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS global_seasons_history (
            season_id INTEGER, user_id INTEGER, weight REAL, rank INTEGER,
            name_cache TEXT, PRIMARY KEY (season_id, user_id)
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS bot_metadata (
            key TEXT PRIMARY KEY, value TEXT
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS hall_da_fama_local (
            season_id INTEGER, chat_id INTEGER, user_id INTEGER,
            peso_temporada_final REAL, rank INTEGER, name_cache TEXT,
            PRIMARY KEY (season_id, chat_id, user_id)
        )''')
        await conn.execute('''CREATE TABLE IF NOT EXISTS duel_cooldowns (
            user_id INTEGER, chat_id INTEGER, last_duel INTEGER,
            PRIMARY KEY (user_id, chat_id)
        )''')

        # Índices para queries de leitura frequente
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_last_seen ON users(last_seen)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_weight_history_timestamp ON weight_history(timestamp)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_weight_history_user_id ON weight_history(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_achievements_user_id ON achievements(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_global_achievements_user_id ON global_achievements(user_id)")

        # Migração: copia achievements legados → global_achievements (dedup por user+name)
        await conn.execute('''
            INSERT OR IGNORE INTO global_achievements (user_id, achievement_name, unlocked_at)
            SELECT user_id, achievement_name, MIN(unlocked_at)
            FROM achievements
            GROUP BY user_id, achievement_name
        ''')
        # Índices compostos para queries frequentes por (user_id, chat_id)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_uid_cid ON users(user_id, chat_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_global_users_uid_sid ON global_users(user_id, season_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_group_meta_uid_cid ON user_group_meta(user_id, chat_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_weight_history_chat_ts ON weight_history(chat_id, timestamp)")

        # Garantias de inicialização
        await conn.execute("INSERT OR IGNORE INTO bot_metadata (key, value) VALUES ('last_archived_season', '1')")

        # Blindagem Suprema para Produção: Garantir que tabelas antigas recebam colunas novas
        await ensure_column(conn, "user_stats", "kg_donated", "REAL DEFAULT 0")
        await ensure_column(conn, "user_stats", "donations_made", "INTEGER DEFAULT 0")
        await ensure_column(conn, "user_stats", "bct_dia_wins", "INTEGER DEFAULT 0")
        await ensure_column(conn, "user_stats", "total_weighs", "INTEGER DEFAULT 0")
        await ensure_column(conn, "global_users", "username", "TEXT")
        await ensure_column(conn, "global_users", "first_name", "TEXT")
        await ensure_column(conn, "global_users", "last_name", "TEXT")

        await conn.commit()
