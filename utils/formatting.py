"""Formatação de pesos, nomes e sanitização HTML."""
import re
import html

ANON = "Anônima"


def display_name(user_or_dict) -> str:
    """
    first_name → username → ANON. Aceita aiogram.User OU dict do DB
    (com chaves 'first_name' / 'username').
    """
    if hasattr(user_or_dict, 'first_name'):
        return user_or_dict.first_name or user_or_dict.username or ANON
    return user_or_dict.get('first_name') or user_or_dict.get('username') or ANON


def format_weight(weight_grams: float) -> str:
    """Peso em gramas → kg com separador de milhar, 2 casas decimais, negrito."""
    weight_kg = weight_grams / 1000.0
    return f"<b>{weight_kg:,.2f}kg</b>"


def format_gain(weight_kg: float) -> str:
    """Ganho de peso com sinal +, separador, negrito."""
    return f"<b>+{weight_kg:,.2f}kg</b>"


def format_name(name: str) -> str:
    """Nome HTML-escaped em negrito."""
    return f"<b>{html.escape(name)}</b>"


_HTML_TAG_RE = re.compile(r'<[^>]+>')


def strip_html(text: str) -> str:
    return _HTML_TAG_RE.sub('', text)
