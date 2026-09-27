import asyncio
from types import SimpleNamespace

from orchestrator.models import Model
from telegram_ai_assistant.config import load_config
from telegram_ai_assistant.document_store import DocumentStore
from telegram_ai_assistant.openai_service import OpenAIService
from telegram_ai_assistant.telegram_handlers import TelegramHandlers


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text="mock document answer")


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


class Message:
    def __init__(self, text):
        self.text = text
        self.replies = []
        self.sent_messages = []

    async def reply_text(self, text, parse_mode=None):
        self.replies.append(text)
        sent = SimpleNamespace(deleted=False)

        async def delete():
            sent.deleted = True

        sent.delete = delete
        self.sent_messages.append(sent)
        return sent


class Update:
    def __init__(self, text):
        self.message = Message(text)
        self.effective_user = SimpleNamespace(id=7)


def test_ask_integration_sends_bounded_context_and_question():
    client = FakeClient()
    config = load_config({"DEMO_MODE": "false", "OPENAI_API_KEY": "test", "REQUIRE_CONFIRMATION_ABOVE_USD": "1"}, dotenv_path=None)
    service = OpenAIService(config, client=client)
    store = DocumentStore()
    store.save("7", "notes.txt", "private document context")
    handlers = TelegramHandlers(None, ai_service=service, document_store=store)
    update = Update("/ask What is here?")
    asyncio.run(handlers.ask(update, None))
    assert any("⏳ Ищу ответ в документе…" in text for text in update.message.replies)
    assert "mock document answer" in update.message.replies
    assert update.message.sent_messages[0].deleted is True
    prompt = client.responses.calls[0]["input"]
    assert "private document context" in prompt
    assert "What is here?" in prompt
    assert client.responses.calls[0]["model"] == Model.LUNA.value
