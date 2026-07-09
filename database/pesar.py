import logging
import random
from datetime import datetime, timedelta

from .pool import get_conn
from .seasons import get_current_season, get_season_label, _archive_previous_season, finalize_local_season
from .users import get_user_meta
from utils import get_streak_multiplier
from config import ALLOWED_USER_ID, GOD_MODE_GROUP_ID, DEV_GROUP_ID


async def record_weight_history(user_id, chat_id, weight_change):
    async with get_conn() as conn:
        await conn.execute(
            'INSERT INTO weight_history (user_id, chat_id, weight_change, timestamp) VALUES (?, ?, ?, ?)',
            (user_id, chat_id, weight_change, int(datetime.now().timestamp())))
        await conn.commit()


async def increment_interactions(user_id, chat_id):
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT count FROM interactions WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        row = await cursor.fetchone()
        if row is None:
            await conn.execute(
                'INSERT INTO interactions (user_id, chat_id, count) VALUES (?, ?, ?)', (user_id, chat_id, 1))
        else:
            await conn.execute(
                'UPDATE interactions SET count = count + 1 WHERE user_id = ? AND chat_id = ?', (user_id, chat_id))
        await conn.commit()


async def _detect_and_finalize_local_reset(chat_id, current_season):
    """Detecta virada de temporada e finaliza ANTES da transação principal.
    Retorna (announcement, last_season_id) ou (None, current_season) se sem reset.
    Separado pra não aninhar conexões dentro de exec_pesar_transaction.

    Read do last_season_id + finalize ficam sob UMA aquisição contínua do lock
    (re-entrante por task — o get_conn() interno de finalize_local_season reusa
    a mesma conexão sem deadlock). Isso fecha a race de virada: dois /pesar
    simultâneos no mesmo grupo não conseguem mais ambos ler last_season antigo e
    o segundo finalize zerar o peso_temporada recém-gravado pelo primeiro.
    """
    async with get_conn() as conn:
        cursor = await conn.execute('SELECT last_season_id FROM groups WHERE chat_id = ?', (chat_id,))
        row = await cursor.fetchone()
        last_local_season = row[0] if row else current_season

        if last_local_season < current_season:
            logging.info(f"Auto-Reset detectado para o grupo {chat_id}. Finalizando temporada {last_local_season}...")
            announcement = await finalize_local_season(chat_id, override_season_id=last_local_season)
            return announcement, last_local_season

    return None, current_season


# --- HIGH PERFORMANCE MEGA TRANSACTION ---
async def exec_pesar_transaction(user_id, chat_id, username, first_name, last_name, group_title, group_username, tier, peso_base, peso_final):
    # Resolver reset de temporada ANTES de abrir txn principal (evita conexões aninhadas).
    _pending_reset = {"announcement": None, "last_season": None}
    if chat_id != 0:
        announcement, last_season = await _detect_and_finalize_local_reset(chat_id, get_current_season())
        _pending_reset["announcement"] = announcement
        _pending_reset["last_season"] = last_season

    async with get_conn() as conn:
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')

        # 0. Busca Meta Local (Piedade + Combo específicos deste Chat)
        meta = await get_user_meta(user_id, chat_id)
        pity = meta["pity"]
        streak = meta["streak"]
        last_date = meta["last_date"]
        max_streak = meta["max_streak"]

        # --- LOGICA DE ATUALIZAÇAO DE META (PITY E STREAK) ---
        async def update_user_group_meta(u_id, c_id, result_tier, n_streak, c_date):
            # PITY: pífio +1, sólido +1 com 50% de chance (≈ +0.5 médio), épico/lendário reseta
            if result_tier == "pifio":
                new_pity = pity + 1
            elif result_tier == "solido":
                new_pity = pity + (1 if random.random() < 0.5 else 0)
            else:  # epico ou lendario
                new_pity = 0

            new_max_streak = n_streak if n_streak > max_streak else max_streak
            await conn.execute('''
                INSERT INTO user_group_meta (user_id, chat_id, pity_counter, streak_count, last_streak_date, max_streak_count)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, chat_id) DO UPDATE SET
                    pity_counter = ?, streak_count = ?, last_streak_date = ?, max_streak_count = ?
            ''', (u_id, c_id, new_pity, n_streak, c_date, new_max_streak, new_pity, n_streak, c_date, new_max_streak))

        # Lógica de Evolução do Combo
        if last_date == yesterday:
            new_streak = streak + 1
        elif last_date == current_date:
            new_streak = streak
        else:
            new_streak = 1

        multiplier = get_streak_multiplier(new_streak)

        # ---------------------------------------------------------
        # CASO 1: PESAGEM GLOBAL (Sazonal)
        # ---------------------------------------------------------
        if chat_id == 0:
            current_season = get_current_season()
            await _archive_previous_season(conn, current_season)

            cursor = await conn.execute(
                'SELECT weight, last_update FROM global_users WHERE user_id = ? AND season_id = ?',
                (user_id, current_season))
            user = await cursor.fetchone()

            if user is not None and user[1] == current_date and user_id != ALLOWED_USER_ID:
                return {"status": "cooldown", "last_update": user[1]}

            current_weight = user[0] if user else 0.0
            is_first_time = (user is None)

            # Peso é em gramas no banco (inteiros)
            weight_change = int(peso_final * 1000)
            new_weight = current_weight + weight_change

            await conn.execute('''
                INSERT INTO global_users (user_id, season_id, weight, last_update, username, first_name, last_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, season_id) DO UPDATE SET
                    weight = excluded.weight, last_update = excluded.last_update,
                    username = excluded.username, first_name = excluded.first_name, last_name = excluded.last_name
            ''', (user_id, current_season, new_weight, current_date, username, first_name, last_name))

            now_ts = int(now.timestamp())
            await conn.execute(
                'INSERT INTO weight_history (user_id, chat_id, weight_change, timestamp) VALUES (?, ?, ?, ?)',
                (user_id, 0, weight_change, now_ts))

            # --- Atualiza Piedade e Streak LOCALIZADO ---
            await update_user_group_meta(user_id, 0, tier, new_streak, current_date)

            # Pega o peso legado específico do Global para exibição (soma de todas as seasons globais)
            cursor = await conn.execute('SELECT SUM(weight) FROM global_users WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()
            new_legado = row[0] if (row and row[0] is not None) else new_weight

            await conn.commit()
            return {
                "status": "success", "kg": peso_final, "base_kg": peso_base, "weight_change": weight_change,
                "multiplier": multiplier, "streak": new_streak, "tier": tier,
                "new_weight": new_weight, "new_legado": new_legado, "is_first_time": is_first_time, "season_id": current_season
            }

        # ---------------------------------------------------------
        # CASO 2: PESAGEM EM GRUPO (Tradicional / Local)
        # ---------------------------------------------------------
        # Reset de temporada já foi resolvido ANTES de abrir esta conexão (ver wrapper).
        current_season = get_current_season()
        reset_announcement = _pending_reset["announcement"]
        last_local_season = _pending_reset["last_season"] or current_season

        await conn.execute(
            'INSERT OR IGNORE INTO groups (chat_id, title, username, last_season_id) VALUES (?, ?, ?, ?)',
            (chat_id, group_title, group_username, current_season))

        cursor = await conn.execute(
            'SELECT peso_legado, peso_temporada, last_update FROM users WHERE user_id = ? AND chat_id = ?',
            (user_id, chat_id))
        user = await cursor.fetchone()

        is_admin_in_debug = (user_id == ALLOWED_USER_ID and (chat_id == GOD_MODE_GROUP_ID or chat_id == DEV_GROUP_ID))

        if not is_admin_in_debug and user is not None and user[2] == current_date:
            return {"status": "cooldown", "last_update": user[2]}

        legado_before = user[0] if user else 0.0
        temporada_before = user[1] if user else 0.0
        is_first_time = (user is None or (legado_before == 0.0 and temporada_before == 0.0))

        weight_change = int(peso_final * 1000)
        new_legado = legado_before + weight_change
        new_temporada = temporada_before + weight_change

        now_ts = int(now.timestamp())
        await conn.execute('''INSERT INTO users (user_id, username, first_name, last_name, chat_id, peso_legado, peso_temporada, last_update, last_seen)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                     ON CONFLICT(user_id, chat_id) DO UPDATE SET
                        peso_legado = excluded.peso_legado, peso_temporada = excluded.peso_temporada,
                        last_update = excluded.last_update, last_seen = excluded.last_seen,
                        username = excluded.username, first_name = excluded.first_name, last_name = excluded.last_name''',
                           (user_id, username, first_name, last_name, chat_id, new_legado, new_temporada, current_date, now_ts))

        await conn.execute(
            'INSERT INTO weight_history (user_id, chat_id, weight_change, timestamp) VALUES (?, ?, ?, ?)',
            (user_id, chat_id, weight_change, now_ts))

        # --- Atualiza Piedade e Streak LOCALIZADO ---
        await update_user_group_meta(user_id, chat_id, tier, new_streak, current_date)

        await conn.commit()
        return {
            "status": "success", "kg": peso_final, "base_kg": peso_base, "weight_change": weight_change,
            "multiplier": multiplier, "streak": new_streak, "tier": tier,
            "new_weight": new_temporada, "new_legado": new_legado, "is_first_time": is_first_time,
            "reset_announcement": reset_announcement, "season_label": get_season_label(last_local_season) if reset_announcement else None
        }


# --- BUCETA DO DIA ---
async def get_daily_winner(chat_id, date_str):
    async with get_conn() as conn:
        cursor = await conn.execute('''
            SELECT u.username, u.first_name, u.last_name, dw.weight_gain, u.user_id
            FROM daily_winners dw
            JOIN users u ON dw.user_id = u.user_id AND dw.chat_id = u.chat_id
            WHERE dw.chat_id = ? AND dw.date = ?
        ''', (chat_id, date_str))
        res = await cursor.fetchone()
    if res:
        return {"username": res[0], "first_name": res[1], "last_name": res[2], "gain": res[3], "user_id": res[4]}
    return None


_BCTDODIA_MIN_ELIGIBLE = 2
_BCTDODIA_EXCLUSION_DAYS = 7


async def draw_daily_winner(chat_id, date_str):
    async with get_conn() as conn:
        try:
            import random as _r
            limit_ts = int(datetime.now().timestamp()) - 259200  # 72h

            # 1) conta todos elegíveis (inclui dono) só pra checar mínimo
            cursor = await conn.execute('''
                SELECT COUNT(DISTINCT user_id)
                FROM weight_history
                WHERE chat_id = ? AND timestamp >= ?
            ''', (chat_id, limit_ts))
            total_all = (await cursor.fetchone() or (0,))[0]

            if total_all < _BCTDODIA_MIN_ELIGIBLE:
                return {"status": "not_enough"}

            # pool real de candidatos (exclui dono — não pode ganhar)
            cursor = await conn.execute('''
                SELECT COUNT(DISTINCT user_id)
                FROM weight_history
                WHERE chat_id = ? AND timestamp >= ? AND user_id != ?
            ''', (chat_id, limit_ts, ALLOWED_USER_ID))
            total = (await cursor.fetchone() or (0,))[0]

            if total == 0:
                return None

            # 2) vencedores recentes (janela de exclusão)
            exclusion_ts = int(datetime.now().timestamp()) - (_BCTDODIA_EXCLUSION_DAYS * 86400)
            cursor = await conn.execute('''
                SELECT user_id FROM daily_winners
                WHERE chat_id = ? AND date >= date('now', ?)
            ''', (chat_id, f'-{_BCTDODIA_EXCLUSION_DAYS} days'))
            recent = {row[0] for row in await cursor.fetchall()}

            # 3) pool filtrado (exclui recentes)
            cursor = await conn.execute('''
                SELECT COUNT(DISTINCT user_id)
                FROM weight_history
                WHERE chat_id = ? AND timestamp >= ? AND user_id != ?
                  AND user_id NOT IN ({})
            '''.format(','.join('?' * len(recent)) if recent else '0'),
                (chat_id, limit_ts, ALLOWED_USER_ID, *recent))
            filtered_total = (await cursor.fetchone() or (0,))[0]

            # 4) fallback: se pool filtrado vazio, usa pool completo
            use_exclusion = filtered_total > 0
            pool_total = filtered_total if use_exclusion else total

            exclusion_clause = (
                f'AND user_id NOT IN ({",".join("?" * len(recent))})'
                if use_exclusion and recent else ''
            )
            exclusion_params = list(recent) if use_exclusion and recent else []

            # 5) sorteia por offset
            offset = _r.randint(0, pool_total - 1)
            cursor = await conn.execute(f'''
                SELECT u.user_id, u.username, u.first_name, u.last_name
                FROM users u
                JOIN (
                    SELECT DISTINCT user_id
                    FROM weight_history
                    WHERE chat_id = ? AND timestamp >= ? AND user_id != ?
                    {exclusion_clause}
                    LIMIT 1 OFFSET ?
                ) w ON w.user_id = u.user_id
                WHERE u.chat_id = ?
                LIMIT 1
            ''', (chat_id, limit_ts, ALLOWED_USER_ID, *exclusion_params, offset, chat_id))
            winner = await cursor.fetchone()

            if not winner:
                return None

            gain = 7.77
            weight_change = int(gain * 1000)

            # 1. Registra o vencedor do dia
            await conn.execute(
                'INSERT INTO daily_winners (date, chat_id, user_id, weight_gain) VALUES (?, ?, ?, ?)',
                (date_str, chat_id, winner[0], gain))

            # 2. Update peso do caboclo (só Legado — temporada é pura, só o /pesar mexe)
            await conn.execute(
                'UPDATE users SET peso_legado = peso_legado + ? WHERE user_id = ? AND chat_id = ?',
                (weight_change, winner[0], chat_id))

            # 6. Salva no histórico
            await conn.execute(
                'INSERT INTO weight_history (user_id, chat_id, weight_change, timestamp) VALUES (?, ?, ?, ?)',
                (winner[0], chat_id, weight_change, int(datetime.now().timestamp())))

            # --- Atualiza Piedade Localizada (Bct do Dia reseta o pity pois é um ganho épico) ---
            new_pity = 0
            await conn.execute('''
                INSERT INTO user_group_meta (user_id, chat_id, pity_counter)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, chat_id) DO UPDATE SET pity_counter = ?
            ''', (winner[0], chat_id, new_pity, new_pity))

            await conn.commit()
            return {"username": winner[1], "first_name": winner[2], "last_name": winner[3], "gain": gain, "user_id": winner[0]}
        except Exception as e:
            logging.error(f"Erro no sorteio (chat={chat_id}, date={date_str}): {e}")
            return None


async def get_today_weight_change(user_id, chat_id) -> int | None:
    """Retorna o weight_change (gramas) da pesagem de hoje do usuário naquele chat, ou None."""
    today_start = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    async with get_conn() as conn:
        cursor = await conn.execute(
            'SELECT weight_change FROM weight_history WHERE user_id = ? AND chat_id = ? AND timestamp >= ? ORDER BY timestamp DESC LIMIT 1',
            (user_id, chat_id, today_start)
        )
        row = await cursor.fetchone()
    return int(row[0]) if row else None
