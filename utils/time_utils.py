"""Utilitários de tempo: cooldown e reset trimestral."""
from datetime import datetime, timedelta


def time_until_next_update() -> str:
    """Tempo humanizado até próxima meia-noite (cooldown do /pesar)."""
    now = datetime.now()
    next_midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
    delta = next_midnight - now

    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    if hours > 0:
        return f"{hours} hora{'s' if hours > 1 else ''} e {minutes} minuto{'s' if minutes > 1 else ''}"
    return f"{minutes} minuto{'s' if minutes > 1 else ''}"


def get_next_reset_date() -> datetime:
    """Data do próximo reset trimestral (01/01, 01/04, 01/07, 01/10)."""
    now = datetime.now()
    month, year = now.month, now.year

    if month < 4:
        return datetime(year, 4, 1)
    if month < 7:
        return datetime(year, 7, 1)
    if month < 10:
        return datetime(year, 10, 1)
    return datetime(year + 1, 1, 1)


def simulate_streak(last_date: str | None, streak: int) -> int:
    """
    Simula o streak que resultaria da próxima pesagem hoje.
    Replica a lógica de exec_pesar_transaction sem side-effects.
    """
    now_str = datetime.now().strftime('%Y-%m-%d')
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    if last_date == yesterday_str:
        return streak + 1
    if last_date == now_str:
        return streak
    return 1
