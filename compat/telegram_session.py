"""Temporary compatibility for Telegram Bot API updates newer than aiogram."""

import logging
from typing import Any

from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import ClientDecodeError


logger = logging.getLogger(__name__)
MAX_CONSECUTIVE_GET_UPDATES_DECODE_ERRORS = 3


def _collect_visible_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(_collect_visible_text(item))
        return result
    if not isinstance(value, dict):
        return []
    for key in ("text", "label", "title"):
        if key in value:
            return _collect_visible_text(value[key])
    result = []
    for item in value.values():
        result.extend(_collect_visible_text(item))
    return result


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

    if value.get("type") == "buttons":
        text = " ".join(_collect_visible_text(value.get("buttons", value)))
        return {"type": "paragraph", "text": [text]}, 1

    downgraded = 0
    for key, item in value.items():
        value[key], item_count = _downgrade_rich_text_buttons(item)
        downgraded += item_count
    return value, downgraded


class TelegramCompatibilitySession(AiohttpSession):
    """Keep polling alive when updates contain unsupported rich messages."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._consecutive_get_updates_decode_errors = 0

    def _record_get_updates_decode_error(self):
        self._consecutive_get_updates_decode_errors += 1
        count = self._consecutive_get_updates_decode_errors
        logger.error(
            "getUpdates decode error %d/%d",
            count,
            MAX_CONSECUTIVE_GET_UPDATES_DECODE_ERRORS,
        )
        if count >= MAX_CONSECUTIVE_GET_UPDATES_DECODE_ERRORS:
            raise SystemExit(
                f"{count} consecutive getUpdates decode errors"
            )

    def check_response(self, bot, method, status_code, content):
        try:
            response = super().check_response(bot, method, status_code, content)
            if method.__api_method__ == "getUpdates":
                self._consecutive_get_updates_decode_errors = 0
            return response
        except ClientDecodeError as original_error:
            if method.__api_method__ != "getUpdates":
                raise

            try:
                payload = self.json_loads(content)
            except Exception:
                self._record_get_updates_decode_error()
                raise original_error from None
            payload, downgraded = _downgrade_rich_text_buttons(payload)
            if not downgraded:
                self._record_get_updates_decode_error()
                raise

            logger.warning(
                "Downgraded %d unsupported RichTextButton node(s) in Telegram updates",
                downgraded,
            )

            response = super().check_response(
                bot,
                method,
                status_code,
                self.json_dumps(payload),
            )
            self._consecutive_get_updates_decode_errors = 0
            return response
