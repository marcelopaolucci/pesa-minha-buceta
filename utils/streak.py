"""Multiplicador de streak (sequência de dias)."""


def get_streak_multiplier(streak_count: int) -> float:
    """Multiplicador baseado na sequência de dias. Cap 1.35x em 30+ dias."""
    if streak_count >= 30:
        return 1.35
    if streak_count >= 20:
        return 1.30
    if streak_count >= 15:
        return 1.25
    if streak_count >= 10:
        return 1.20
    if streak_count >= 7:
        return 1.15
    if streak_count >= 5:
        return 1.10
    if streak_count >= 3:
        return 1.05
    return 1.0
