import asyncio
from types import SimpleNamespace

from telegram_ai_assistant.config import load_config
from telegram_ai_assistant.document_store import DocumentStore
from telegram_ai_assistant.handlers import AssistantHandlers
from telegram_ai_assistant.telegram_handlers import TelegramHandlers


class Message:
    def __init__(self, text=""):
        self.text = text
        self.replies = []
        self.document = None

    async def reply_text(self, text):
        self.replies.append(text)


class Update:
    def __init__(self, user_id, text=""):
        self.effective_user = SimpleNamespace(id=user_id)
        self.message = Message(text)


def run(awaitable):
    return asyncio.run(awaitable)


def make_handlers(store=None):
    config = load_config({"DEMO_MODE": "true", "OPENAI_MODEL_DEFAULT": "gpt-6-luna"}, dotenv_path=None)
    return TelegramHandlers(AssistantHandlers(config), document_store=store or DocumentStore())


def test_clear_removes_only_current_user_document():
    store = DocumentStore()
    store.save("one", "a.txt", "one")
    store.save("two", "b.txt", "two")
    handlers = make_handlers(store)
    update = Update("one", "/clear")
    run(handlers.clear(update, None))
    assert update.message.replies == ["Документ удалён."]
    assert store.has_document("one") is False
    assert store.has_document("two") is True


def test_clear_without_document_is_safe():
    handlers = make_handlers()
    update = Update("one", "/clear")
    run(handlers.clear(update, None))
    assert update.message.replies == ["Активный документ не найден."]


def test_status_contains_only_safe_state():
    store = DocumentStore()
    store.save("one", "private.txt", "secret contents")
    handlers = make_handlers(store)
    update = Update("one", "/status")
    run(handlers.status(update, None))
    status = update.message.replies[0]
    assert "DEMO_MODE" in status
    assert "загружен" in status
    assert "private.txt" not in status
    assert "secret contents" not in status
    assert "one" not in status
    assert "OPENAI" not in status
