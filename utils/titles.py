"""Patente e emoji de ranking baseados em conquistas."""
from utils.emojis import Emojis


_WEIGHT_HIERARCHY = ["bcto_1000", "bcto_800", "bcto_500", "bcto_250", "bcto_100", "bcto_50", "first_weigh"]


def get_rank_emoji(rank_val) -> str:
    r = str(rank_val)
    if r == "1":
        return Emojis.MEDALHA_1
    if r == "2":
        return Emojis.MEDALHA_2
    if r == "3":
        return Emojis.MEDALHA_3
    return Emojis.TROFEU


def get_user_title(achievements) -> str:
    """Patente do usuário baseada na maior conquista de peso."""
    # Lazy imports para evitar ciclos (achievements_manager depende de database)
    from utils.achievements_manager import ACHIEVEMENTS_DEFS
    from utils.messages import Messages

    title = Messages.Profile.CLANDESTINA  # fallback
    for ach_key in _WEIGHT_HIERARCHY:
        if ach_key in achievements:
            ach_data = ACHIEVEMENTS_DEFS.get(ach_key)
            if not ach_data:
                continue
            tier_str = ach_data.get("tier", "")
            parts = tier_str.split("</tg-emoji>")
            emoji = (parts[0] + "</tg-emoji>") if len(parts) >= 2 else tier_str
            name = ach_data.get("name", ach_key)
            title = f"{name} {emoji}‎"
            break
    return title
