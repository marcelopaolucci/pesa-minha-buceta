import asyncio

import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock

import handlers.duelar as duelar
from handlers.duelar import resolve_duel_stake


@pytest.mark.parametrize(
    ("argument", "expected_grams"),
    [
        (None, 2500.0),
        ("", 2500.0),
        ("5", 5000.0),
        ("0.5kg", 500.0),
        ("500g", 500.0),
    ],
)
def test_resolve_duel_stake_supports_default_and_custom_weights(
    argument, expected_grams
):
    assert resolve_duel_stake(argument) == expected_grams


@pytest.mark.parametrize(
    "argument", ["0", "-1", "peso", "nan", "NaNkg", "inf", "Infinitykg", "1e309"]
)
def test_resolve_duel_stake_rejects_non_positive_or_malformed_weights(argument):
    with pytest.raises((TypeError, ValueError)):
        resolve_duel_stake(argument)


class _CompletedTask:
    def add_done_callback(self, callback):
        callback(self)


def _finish_immediately(coroutine):
    coroutine.close()
    return _CompletedTask()


def test_cmd_duelar_saves_and_announces_the_custom_stake(monkeypatch):
    sent_message = SimpleNamespace(message_id=99)
    message = SimpleNamespace(
        chat=SimpleNamespace(id=-10),
        from_user=SimpleNamespace(id=1, first_name="Ana"),
        reply=AsyncMock(return_value=sent_message),
    )
    save_duel = AsyncMock()
    monkeypatch.setattr(duelar, "is_group_chat", AsyncMock(return_value=True))
    monkeypatch.setattr(duelar, "get_duel_cooldown", AsyncMock(return_value=None))
    monkeypatch.setattr(duelar, "get_peso_legado", AsyncMock(return_value=1000.0))
    monkeypatch.setattr(duelar, "save_duel", save_duel)
    monkeypatch.setattr(duelar, "set_duel_cooldown", AsyncMock())
    monkeypatch.setattr(duelar.asyncio, "create_task", _finish_immediately)

    asyncio.run(duelar.cmd_duelar(message, SimpleNamespace(args="500g")))

    assert "<b>0.50kg</b>" in message.reply.await_args.args[0]
    assert save_duel.await_args.kwargs["stake"] == 500.0


def test_cmd_duelar_rejects_custom_stake_above_balance(monkeypatch):
    message = SimpleNamespace(
        chat=SimpleNamespace(id=-10),
        from_user=SimpleNamespace(id=1, first_name="Ana"),
        reply=AsyncMock(),
    )
    save_duel = AsyncMock()
    monkeypatch.setattr(duelar, "is_group_chat", AsyncMock(return_value=True))
    monkeypatch.setattr(duelar, "get_duel_cooldown", AsyncMock(return_value=None))
    monkeypatch.setattr(duelar, "get_peso_legado", AsyncMock(return_value=3000.0))
    monkeypatch.setattr(duelar, "save_duel", save_duel)

    asyncio.run(duelar.cmd_duelar(message, SimpleNamespace(args="5kg")))

    save_duel.assert_not_awaited()
    assert "<b>5.00kg</b>" in message.reply.await_args.args[0]


def test_callback_duelo_transfers_the_persisted_stake(monkeypatch):
    callback_message = SimpleNamespace(
        message_id=99,
        edit_text=AsyncMock(),
        delete=AsyncMock(),
    )
    callback = SimpleNamespace(
        data="duel_accept",
        message=callback_message,
        from_user=SimpleNamespace(id=2, first_name="Bia"),
        bot=object(),
        answer=AsyncMock(),
    )
    transfer = AsyncMock()
    monkeypatch.setattr(
        duelar,
        "get_duel",
        AsyncMock(
            return_value={
                "challenger_id": 1,
                "challenger_name": "Ana",
                "chat_id": -10,
                "stake": 500.0,
                "timestamp": duelar.time.time(),
            }
        ),
    )
    monkeypatch.setattr(
        duelar, "get_peso_legado_or_none", AsyncMock(side_effect=[700.0, 800.0])
    )
    monkeypatch.setattr(duelar, "delete_duel", AsyncMock())
    monkeypatch.setattr(duelar, "transfer_duel_weight", transfer)
    monkeypatch.setattr(duelar, "increment_stat", AsyncMock())
    monkeypatch.setattr(duelar, "check_achievements", AsyncMock())
    monkeypatch.setattr(duelar.secrets, "choice", lambda sides: "challenger")

    asyncio.run(duelar.callback_duelo(callback))

    transfer.assert_awaited_once_with(1, 2, -10, 500.0)
    assert "<b>0.50kg</b>" in callback_message.edit_text.await_args.args[0]
