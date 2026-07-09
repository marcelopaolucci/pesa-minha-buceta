"""
Facade dos utilitários. Re-exporta tudo para compatibilidade com
`from utils import X`. Implementações divididas por domínio nos submódulos.
"""

from .rng import TIERS, TIER_RANGES, get_tier_weights, roll_weighted_kg
from .formatting import format_weight, format_gain, format_name, strip_html, display_name, ANON
from .parsing import parse_weight_to_grams
from .time_utils import time_until_next_update, get_next_reset_date, simulate_streak
from .streak import get_streak_multiplier
from .titles import get_rank_emoji, get_user_title
from .chat import is_group_chat
from .builders import safe_edit, parse_cb

__all__ = [
    # rng
    "TIERS", "TIER_RANGES", "get_tier_weights", "roll_weighted_kg",
    # formatting
    "format_weight", "format_gain", "format_name", "strip_html", "display_name", "ANON",
    # parsing
    "parse_weight_to_grams",
    # time
    "time_until_next_update", "get_next_reset_date", "simulate_streak",
    # streak
    "get_streak_multiplier",
    # titles
    "get_rank_emoji", "get_user_title",
    # chat
    "is_group_chat",
    # builders
    "safe_edit", "parse_cb",
]
