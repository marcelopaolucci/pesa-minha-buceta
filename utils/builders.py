"""
Helpers de UI para callbacks Telegram.
Centraliza padrões repetidos: edição segura de mensagens e parsing de callback_data.
"""
import logging
from typing import Optional
from aiogram.types import CallbackQuery, InlineKeyboardMarkup


async def safe_edit(
    callback: CallbackQuery,
    text: str,
    *,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: str = 'HTML',
) -> bool:
    """
    Edita mensagem do callback. Silencia exceções (expirada, conteúdo idêntico, etc).
    Retorna True se editou, False se falhou.
    """
    try:
        await callback.message.edit_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
        return True
    except Exception as e:
        logging.debug(f"safe_edit falhou: {e}")
        return False


def parse_cb(data: str, *fields: str) -> Optional[dict]:
    """
    Parseia callback_data 'prefix:val1:val2:...' em dict.

    Args:
        data: string de callback_data (ex: 'pesar_btn:local:123:456').
        fields: nomes dos campos a partir do índice 1.
                Prefixe com 'int:' para coerção de inteiro.

    Returns:
        dict com os campos parseados, ou None se a string não bateu (curta demais
        ou conversão de inteiro falhou).

    Exemplo:
        >>> parse_cb('pesar_btn:local:123:456', 'view', 'int:chat_id', 'int:user_id')
        {'view': 'local', 'chat_id': 123, 'user_id': 456}
        >>> parse_cb('pesar_btn:local', 'view', 'int:chat_id')
        None
    """
    parts = data.split(":")
    if len(parts) < len(fields) + 1:
        return None
    out = {}
    for i, key in enumerate(fields, start=1):
        raw = parts[i]
        if key.startswith("int:"):
            try:
                out[key[4:]] = int(raw)
            except ValueError:
                return None
        else:
            out[key] = raw
    return out
