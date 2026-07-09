"""
Camada de acesso a dados.

Este módulo é um *facade*: toda função pública continua importável via
`from database import X` ou `database.X` para manter compatibilidade
com o código existente. As implementações estão agora divididas por
domínio em submódulos (pool, schema, seasons, users, groups, rankings,
pesar, achievements, stats, duels).
"""

from .pool import DB_FILE, get_conn, ensure_column, init_pool, close_pool
from .schema import init_db
from .seasons import (
    get_current_season,
    get_season_label,
    finalize_local_season,
    get_hall_of_fame,
    get_available_seasons,
    get_hall_of_fame_local,
)
from .users import (
    update_user,
    update_activity,
    get_user_name,
    can_update,
    get_peso_legado,
    get_peso_legado_or_none,
    get_peso_temporada,
    get_global_weight,
    get_local_rank,
    get_global_rank,
    get_global_legado_rank,
    reset_user,
    get_user_groups,
    get_user_meta,
    inject_weight,
    transfer_donation,
)
from .groups import (
    get_all_groups,
    delete_group,
    upsert_group,
)
from .rankings import (
    get_leaderboard,
    get_weekly_ranking,
    get_monthly_ranking,
)
from .pesar import (
    record_weight_history,
    increment_interactions,
    exec_pesar_transaction,
    get_daily_winner,
    draw_daily_winner,
    get_today_weight_change,
)
from .achievements import (
    register_achievement,
    get_achievements,
    get_global_achievements,
    register_global_achievement,
    get_global_achievements_list,
)
from .stats import (
    increment_stat,
    get_user_stats,
    get_global_user_stats,
    get_global_peso_legado_total,
    get_global_legado_historico,
    get_groups_count,
    get_total_system_data,
    get_total_weighs_from_history,
    get_local_weighs_count,
    get_total_local_legado_sum,
    EMPTY_STATS,
)
from .duels import (
    save_duel,
    get_duel,
    delete_duel,
    get_duel_cooldown,
    set_duel_cooldown,
    transfer_duel_weight,
)

__all__ = [
    # pool
    "DB_FILE", "get_conn", "ensure_column", "init_pool", "close_pool",
    # schema
    "init_db",
    # seasons
    "get_current_season", "get_season_label", "finalize_local_season",
    "get_hall_of_fame", "get_available_seasons", "get_hall_of_fame_local",
    # users
    "update_user", "update_activity", "get_user_name", "can_update",
    "get_peso_legado", "get_peso_legado_or_none", "get_peso_temporada", "get_global_weight",
    "get_local_rank", "get_global_rank", "get_global_legado_rank", "reset_user",
    "get_user_groups", "get_user_meta", "inject_weight", "transfer_donation",
    # groups
    "get_all_groups", "delete_group", "upsert_group",
    # rankings
    "get_leaderboard", "get_weekly_ranking", "get_monthly_ranking",
    # pesar
    "record_weight_history", "increment_interactions",
    "exec_pesar_transaction", "get_daily_winner", "draw_daily_winner", "get_today_weight_change",
    # achievements
    "register_achievement", "get_achievements", "get_global_achievements",
    "register_global_achievement", "get_global_achievements_list",
    # stats
    "increment_stat", "get_user_stats", "get_global_user_stats",
    "get_global_peso_legado_total", "get_global_legado_historico", "get_groups_count", "get_total_system_data",
    "get_total_weighs_from_history", "get_local_weighs_count", "get_total_local_legado_sum", "EMPTY_STATS",
    # duels
    "save_duel", "get_duel", "delete_duel", "get_duel_cooldown", "set_duel_cooldown", "transfer_duel_weight",
]
