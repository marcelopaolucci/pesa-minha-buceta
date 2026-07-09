"""Motor RNG do Pesar. SAGRADO — balanceamento do jogo."""
import random

TIERS = ["pifio", "solido", "epico", "lendario"]
TIER_RANGES = {
    "pifio":    (1.00, 3.00),
    "solido":   (3.00, 6.00),
    "epico":    (6.00, 9.00),
    "lendario": (9.00, 12.00),
}


def get_tier_weights(pity_level: int) -> list[float]:
    """Retorna probabilidades [pifio, solido, epico, lendario] baseadas no pity."""
    if pity_level >= 5:
        return [0.00, 0.00, 0.10, 0.90]
    if pity_level >= 3:
        return [0.10, 0.50, 0.35, 0.05]
    return [0.40, 0.45, 0.12, 0.03]


def roll_weighted_kg(pity_level: int = 0) -> dict:
    """
    Motor RNG V3.0: Rola tier + peso base float.
    Retorna: {"tier": str, "peso_base": float}
    """
    weights = get_tier_weights(pity_level)
    tier = random.choices(TIERS, weights=weights, k=1)[0]
    low, high = TIER_RANGES[tier]
    peso_base = round(random.uniform(low, high), 2)
    return {"tier": tier, "peso_base": peso_base}
