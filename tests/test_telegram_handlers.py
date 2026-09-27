import asyncio

import pytest

from telegram_ai_assistant.config import load_config
from telegram_ai_assistant.handlers import AssistantHandlers
from telegram_ai_assistant.telegram_handlers import TelegramHandlers


class FakeMessage:
    def __init__(self, text=None):
        self.text = text
        self.replies = []

    async def reply_text(self, text, parse_mode=None):
        self.replies.append(text)


class FakeUpdate:
    def __init__(self, text=None):
        self.message = FakeMessage(text)


@pytest.fixture
def telegram_handlers():
    config = load_config({"DEMO_MODE": "true", "MAX_MESSAGE_LENGTH": "10"}, dotenv_path=None)
    return TelegramHandlers(AssistantHandlers(config))


def run(coroutine):
    return asyncio.run(coroutine)


def test_start_and_help_handlers(telegram_handlers):
    start_update = FakeUpdate()
    help_update = FakeUpdate()
    run(telegram_handlers.start(start_update, None))
    run(telegram_handlers.help(help_update, None))
    assert "<code>/help</code>" in start_update.message.replies[0]
    assert "<code>/help" in help_update.message.replies[0]


def test_text_handler_returns_demo_reply(telegram_handlers):
    update = FakeUpdate("Привет")
    run(telegram_handlers.text(update, None))
    assert "Демо-ответ" in update.message.replies[0]


def test_text_handler_converts_length_error(telegram_handlers):
    update = FakeUpdate("x" * 11)
    run(telegram_handlers.text(update, None))
    assert "слишком длинное" in update.message.replies[0]
