"""Temporary compatibility for Telegram Bot API updates newer than aiogram."""

import logging
from typing import Any

from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import ClientDecodeError


logger = logging.getLogger(__name__)


def _downgrade_rich_text_buttons(value: Any) -> tuple[Any, int]:
    """Replace Bot API 10.3 RichTextButton nodes with their visible text."""
    if isinstance(value, list):
        downgraded = 0
        for index, item in enumerate(value):
            value[index], item_count = _downgrade_rich_text_buttons(item)
            downgraded += item_count
        return value, downgraded

    if not isinstance(value, dict):
        return value, 0

    if value.get("type") == "button" and isinstance(value.get("button"), dict):
        text, nested_count = _downgrade_rich_text_buttons(
            value["button"].get("text", "")
        )
        return text, nested_count + 1

    downgraded = 0
    for key, item in value.items():
        value[key], item_count = _downgrade_rich_text_buttons(item)
        downgraded += item_count
    return value, downgraded


class TelegramCompatibilitySession(AiohttpSession):
    """Keep polling alive when updates contain unsupported rich messages."""

    def check_response(self, bot, method, status_code, content):
        try:
            return super().check_response(bot, method, status_code, content)
        except ClientDecodeError as original_error:
            if method.__api_method__ != "getUpdates":
                raise

            try:
                payload = self.json_loads(content)
            except Exception:
                raise original_error from None
            payload, downgraded = _downgrade_rich_text_buttons(payload)
            if not downgraded:
                raise

            logger.warning(
                "Downgraded %d unsupported RichTextButton node(s) in Telegram updates",
                downgraded,
            )

            return super().check_response(
                bot,
                method,
                status_code,
                self.json_dumps(payload),
            )
