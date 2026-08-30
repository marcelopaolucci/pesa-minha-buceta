import importlib
import json

import pytest
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import ClientDecodeError
from aiogram.methods import GetUpdates, SendMessage


def _load_compatibility_session():
    try:
        module = importlib.import_module("compat.telegram_session")
    except ModuleNotFoundError:
        pytest.fail("the Telegram compatibility session is missing", pytrace=False)
    return module.TelegramCompatibilitySession


def _get_updates_payload(rich_message):
    return {
        "ok": True,
        "result": [
            {
                "update_id": 1002408676,
                "message": {
                    "message_id": 9963782,
                    "date": 1787588482,
                    "chat": {"id": -1001352305515, "type": "supergroup"},
                    "text": "mensagem atual",
                    "reply_to_message": {
                        "message_id": 9963781,
                        "date": 1787588479,
                        "chat": {"id": -1001352305515, "type": "supergroup"},
                        "rich_message": rich_message,
                    },
                },
            }
        ],
    }


def _rich_message_with_button():
    return {
        "blocks": [
            {
                "type": "paragraph",
                "text": [
                    "tem como adicionar ",
                    {
                        "type": "button",
                        "button": {
                            "text": "botão",
                            "style": "primary",
                            "url": "tg://user?id=1660418407",
                        },
                    },
                    " nas mensagens agr",
                ],
            }
        ]
    }


def _supported_rich_message():
    return {
        "blocks": [
            {
                "type": "paragraph",
                "text": [
                    "texto ",
                    {"type": "bold", "text": "compatível"},
                ],
            }
        ]
    }


def _rich_message_with_buttons_block():
    return {
        "blocks": [
            {
                "type": "buttons",
                "buttons": [
                    {"text": "Perfil", "url": "https://example.com/perfil"},
                    {"text": "Ranking", "url": "https://example.com/ranking"},
                ],
            }
        ]
    }


def test_stock_session_rejects_rich_text_button():
    session = AiohttpSession()
    bot = Bot("123456:abcdefghijklmnopqrstuvwxyzABCDEFG")
    payload = _get_updates_payload(_rich_message_with_button())

    with pytest.raises(ClientDecodeError):
        session.check_response(
            bot=bot,
            method=GetUpdates(),
            status_code=200,
            content=json.dumps(payload),
        )


def test_get_updates_downgrades_only_nested_rich_text_button():
    session = _load_compatibility_session()()
    bot = Bot("123456:abcdefghijklmnopqrstuvwxyzABCDEFG")
    payload = _get_updates_payload(_rich_message_with_button())

    response = session.check_response(
        bot=bot,
        method=GetUpdates(),
        status_code=200,
        content=json.dumps(payload),
    )

    update = response.result[0]
    assert update.update_id == 1002408676
    assert update.message.text == "mensagem atual"
    paragraph = update.message.reply_to_message.rich_message.blocks[0]
    assert paragraph.model_dump(exclude_none=True)["text"] == [
        "tem como adicionar ",
        "botão",
        " nas mensagens agr",
    ]


def test_get_updates_downgrades_rich_text_buttons_block():
    session = _load_compatibility_session()()
    bot = Bot("123456:abcdefghijklmnopqrstuvwxyzABCDEFG")
    payload = _get_updates_payload(_rich_message_with_buttons_block())

    response = session.check_response(
        bot=bot,
        method=GetUpdates(),
        status_code=200,
        content=json.dumps(payload),
    )

    block = response.result[0].message.reply_to_message.rich_message.blocks[0]
    assert block.model_dump(exclude_none=True)["text"] == ["Perfil Ranking"]


def test_get_updates_preserves_supported_rich_message():
    session = _load_compatibility_session()()
    bot = Bot("123456:abcdefghijklmnopqrstuvwxyzABCDEFG")
    payload = _get_updates_payload(_supported_rich_message())

    response = session.check_response(
        bot=bot,
        method=GetUpdates(),
        status_code=200,
        content=json.dumps(payload),
    )

    paragraph = response.result[0].message.reply_to_message.rich_message.blocks[0]
    assert paragraph.model_dump(exclude_none=True)["text"] == [
        "texto ",
        {"type": "bold", "text": "compatível"},
    ]


def test_non_get_updates_response_is_not_sanitized():
    session = _load_compatibility_session()()
    bot = Bot("123456:abcdefghijklmnopqrstuvwxyzABCDEFG")
    message = _get_updates_payload(_rich_message_with_button())["result"][0]["message"]
    payload = {"ok": True, "result": message}

    with pytest.raises(ClientDecodeError):
        session.check_response(
            bot=bot,
            method=SendMessage(chat_id=1, text="teste"),
            status_code=200,
            content=json.dumps(payload),
        )


def test_get_updates_reraises_unhandled_decode_error():
    session = _load_compatibility_session()()
    bot = Bot("123456:abcdefghijklmnopqrstuvwxyzABCDEFG")
    unsupported_rich_message = {
        "blocks": [
            {
                "type": "paragraph",
                "text": [{"type": "future_type", "text": "desconhecido"}],
            }
        ]
    }
    payload = _get_updates_payload(unsupported_rich_message)

    with pytest.raises(ClientDecodeError):
        session.check_response(
            bot=bot,
            method=GetUpdates(),
            status_code=200,
            content=json.dumps(payload),
        )


def test_get_updates_keeps_client_decode_error_for_malformed_json():
    session = _load_compatibility_session()()
    bot = Bot("123456:abcdefghijklmnopqrstuvwxyzABCDEFG")

    with pytest.raises(ClientDecodeError):
        session.check_response(
            bot=bot,
            method=GetUpdates(),
            status_code=200,
            content="{malformed",
        )


def test_get_updates_exits_after_three_consecutive_decode_errors(monkeypatch):
    session = _load_compatibility_session()()
    bot = Bot("123456:abcdefghijklmnopqrstuvwxyzABCDEFG")

    def always_fail(*args, **kwargs):
        raise ClientDecodeError("decode failed", ValueError("decode failed"), {})

    monkeypatch.setattr(AiohttpSession, "check_response", always_fail)

    with pytest.raises(SystemExit, match="3 consecutive getUpdates decode errors"):
        for attempt in range(3):
            if attempt < 2:
                with pytest.raises(ClientDecodeError):
                    session.check_response(
                        bot=bot,
                        method=GetUpdates(),
                        status_code=200,
                        content="{}",
                    )
                continue
            session.check_response(
                bot=bot,
                method=GetUpdates(),
                status_code=200,
                content="{}",
            )


def test_successful_get_updates_resets_decode_error_streak(monkeypatch):
    session = _load_compatibility_session()()
    bot = Bot("123456:abcdefghijklmnopqrstuvwxyzABCDEFG")
    calls = 0

    def fail_once_then_succeed(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls in (1, 2, 4):
            raise ClientDecodeError("decode failed", ValueError("decode failed"), {})
        return {"ok": True, "result": []}

    monkeypatch.setattr(AiohttpSession, "check_response", fail_once_then_succeed)

    for attempt in range(4):
        if attempt in (0, 1, 3):
            with pytest.raises(ClientDecodeError):
                session.check_response(
                    bot=bot,
                    method=GetUpdates(),
                    status_code=200,
                    content="{}",
                )
            continue
        session.check_response(
            bot=bot,
            method=GetUpdates(),
            status_code=200,
            content="{}",
        )


def test_bot_is_created_with_compatibility_session():
    import bot as bot_module

    assert hasattr(bot_module, "create_bot"), "bot factory is missing"

    application_bot = bot_module.create_bot(
        "123456:abcdefghijklmnopqrstuvwxyzABCDEFG"
    )

    assert isinstance(application_bot.session, _load_compatibility_session())
