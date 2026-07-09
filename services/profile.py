"""Snapshot de perfil agregado + builder de texto.

Junta 9 queries do perfil em 1 conn única (sequencial mas sem overhead
de abrir/fechar aiosqlite a cada call). Texto montado a partir de
`Messages.Profile.get_profile_text` (sagrado).
"""
import html
from database import (get_peso_legado, get_peso_temporada, get_user_stats,
                      get_global_achievements_list, get_groups_count, get_global_weight,
                      get_local_rank, get_global_rank, get_global_legado_rank,
                      get_global_user_stats, get_global_peso_legado_total,
                      get_global_legado_historico, get_total_weighs_from_history,
                      get_local_weighs_count, get_total_local_legado_sum, EMPTY_STATS)
from utils import format_weight, get_user_title, get_rank_emoji
from utils.messages import Messages
from utils.achievements_manager import ACHIEVEMENTS_DEFS
from utils.emojis import Emojis
from config import ALLOWED_USER_ID


def _owner_zero_snapshot(*, global_view: bool = False) -> dict:
    """Snapshot vazio (zerado) usado para o dono do bot — esconde do ranking."""
    base = {
        "peso_legado": 0,
        "peso_temporada": 0,
        "stats": dict(EMPTY_STATS),
        "local_rank": "—",
        "local_legado_rank": "—",
    }
    if global_view:
        base.update({
            "achievements": [],
            "groups_count": 0,
            "total_weighs": 0,
            "total_legado_sum": 0.0,
        })
    else:
        base["local_weighs"] = 0
    return base


async def get_profile_snapshot(user_id: int, chat_id: int) -> dict:
    """
    Coleta todos os dados necessários para o perfil de um usuário.
    Retorna dict pronto para `build_profile_text`.
    """
    if user_id == ALLOWED_USER_ID:
        return _owner_zero_snapshot()

    peso_legado = await get_peso_legado(user_id, chat_id)
    peso_temporada = await get_peso_temporada(user_id, chat_id)
    stats = await get_user_stats(user_id, chat_id)
    local_rank = await get_local_rank(user_id, chat_id, column="peso_temporada")
    local_legado_rank = await get_local_rank(user_id, chat_id, column="peso_legado")
    local_weighs = await get_local_weighs_count(user_id, chat_id)

    return {
        "peso_legado": peso_legado,
        "peso_temporada": peso_temporada,
        "stats": stats,
        "local_rank": local_rank,
        "local_legado_rank": local_legado_rank,
        "local_weighs": local_weighs,
    }


async def get_global_profile_snapshot(user_id: int) -> dict:
    """Coleta dados globais do usuário para a view global do perfil."""
    if user_id == ALLOWED_USER_ID:
        return _owner_zero_snapshot(global_view=True)
    peso_temporada = await get_global_weight(user_id)
    peso_legado = await get_global_legado_historico(user_id)
    global_rank_temporada = await get_global_rank(user_id)
    global_rank_legado = await get_global_legado_rank(user_id)
    stats = await get_global_user_stats(user_id)
    _raw_achievements = await get_global_achievements_list(user_id)
    achievements = [a for a in _raw_achievements if a in ACHIEVEMENTS_DEFS]
    groups_count = await get_groups_count(user_id)
    total_weighs = await get_total_weighs_from_history(user_id)
    total_legado_sum = await get_total_local_legado_sum(user_id)
    return {
        "peso_temporada": peso_temporada,
        "peso_legado": peso_legado,
        "stats": stats,
        "achievements": achievements,
        "groups_count": groups_count,
        "local_rank": global_rank_temporada,
        "local_legado_rank": global_rank_legado,
        "total_weighs": total_weighs,
        "total_legado_sum": total_legado_sum,
    }


def build_global_profile_text(snapshot: dict, display_name: str) -> str:
    stats = snapshot["stats"]
    local_rank = snapshot["local_rank"]
    local_legado_rank = snapshot["local_legado_rank"]
    local_rank_str = str(local_rank) if str(local_rank).isdigit() else local_rank
    local_legado_rank_str = str(local_legado_rank) if str(local_legado_rank).isdigit() else local_legado_rank
    return Messages.Profile.get_global_profile_text(
        name=html.escape(display_name),
        group_emoji=Emojis.PLANETA,
        group_title="Telegram Global",
        weight=format_weight(snapshot["peso_temporada"]),
        legado_weight=format_weight(snapshot["peso_legado"]),
        local_rank=local_rank_str,
        local_legado_rank=local_legado_rank_str,
        duels_won=stats.get("duels_won", 0),
        duels_lost=stats.get("duels_lost", 0),
        kg_donated=stats.get("kg_donated", 0.0),
        bct_dia_wins=stats.get("bct_dia_wins", 0),
        total_weighs=snapshot.get("total_weighs", 0),
        achievements_count=len(snapshot.get("achievements", [])),
        groups_count=snapshot.get("groups_count", 0),
    )


def build_profile_text(snapshot: dict, display_name: str, group_title: str) -> str:
    stats = snapshot["stats"]
    local_rank = snapshot["local_rank"]
    local_legado_rank = snapshot["local_legado_rank"]
    local_rank_str = str(local_rank) if str(local_rank).isdigit() else local_rank
    local_legado_rank_str = str(local_legado_rank) if str(local_legado_rank).isdigit() else local_legado_rank
    return Messages.Profile.get_profile_text(
        name=html.escape(display_name),
        group_emoji=Emojis.LOCAL_HEADER,
        group_title=html.escape(group_title or ""),
        weight=format_weight(snapshot["peso_temporada"]),
        legado_weight=format_weight(snapshot["peso_legado"]),
        local_rank=local_rank_str,
        local_legado_rank=local_legado_rank_str,
        duels_won=stats.get("duels_won", 0),
        duels_lost=stats.get("duels_lost", 0),
        kg_donated=stats.get("kg_donated", 0.0),
        bct_dia_wins=stats.get("bct_dia_wins", 0),
        local_weighs=snapshot.get("local_weighs", 0),
    )
