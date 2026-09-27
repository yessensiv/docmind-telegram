import asyncio
from types import SimpleNamespace

from orchestrator.models import Model
from telegram_ai_assistant.config import load_config
from telegram_ai_assistant.handlers import AssistantHandlers
from telegram_ai_assistant.openai_service import OpenAIService
from telegram_ai_assistant.telegram_handlers import TelegramHandlers


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text="**Elden Ring** — action RPG")


class FakeMessage:
    def __init__(self, text):
        self.text = text
        self.replies = []
        self.sent = []

    async def reply_text(self, text, parse_mode=None):
        self.replies.append(text)
        message = SimpleNamespace(deleted=False)

        async def delete():
            message.deleted = True

        message.delete = delete
        self.sent.append(message)
        return message


class FakeUpdate:
    def __init__(self, text):
        self.message = FakeMessage(text)
        self.effective_user = SimpleNamespace(id=11)


def test_chat_without_text_shows_hint():
    config = load_config({"DEMO_MODE": "true"}, dotenv_path=None)
    update = FakeUpdate("/chat")
    asyncio.run(TelegramHandlers(AssistantHandlers(config)).chat(update, None))
    assert "Использование:" in update.message.replies[0]
    assert "<code>/chat" in update.message.replies[0]


def test_demo_chat_does_not_call_openai():
    config = load_config({"DEMO_MODE": "true"}, dotenv_path=None)
    update = FakeUpdate("/chat привет")
    handlers = AssistantHandlers(config)
    asyncio.run(TelegramHandlers(handlers).chat(update, None))
    assert "Демо-ответ" in update.message.replies[0]


def test_production_chat_uses_policy_and_prompt_without_document_context():
    config = load_config({"DEMO_MODE": "false", "OPENAI_API_KEY": "test", "REQUIRE_CONFIRMATION_ABOVE_USD": "1"}, dotenv_path=None)
    client = SimpleNamespace(responses=FakeResponses())
    service = OpenAIService(config, client=client)
    update = FakeUpdate("/chat объясни задачу")
    asyncio.run(TelegramHandlers(None, ai_service=service).chat(update, None))
    assert update.message.replies[0] == "⏳ Обрабатываю запрос…"
    assert "<b>Elden Ring</b> — action RPG" in update.message.replies[1]
    assert client.responses.calls[0]["model"] == Model.LUNA.value
    assert "объясни задачу" in client.responses.calls[0]["input"]
    assert "КОНТЕКСТ ДОКУМЕНТА" not in client.responses.calls[0]["input"]
    assert update.message.sent[0].deleted is True
