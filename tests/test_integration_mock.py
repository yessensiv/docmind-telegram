import asyncio
from types import SimpleNamespace

from orchestrator.models import Model
from telegram_ai_assistant.config import load_config
from telegram_ai_assistant.openai_service import OpenAIService
from telegram_ai_assistant.telegram_handlers import TelegramHandlers


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text="mocked production answer")


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


class FakeMessage:
    def __init__(self, text=None, document=None):
        self.text = text
        self.document = document
        self.replies = []
        self.sent_messages = []

    async def reply_text(self, text, reply_markup=None, parse_mode=None):
        self.replies.append((text, reply_markup))
        sent = SimpleNamespace(deleted=False)

        async def delete():
            sent.deleted = True

        sent.delete = delete
        self.sent_messages.append(sent)
        return sent


class FakeUpdate:
    def __init__(self, text=None, document=None):
        self.message = FakeMessage(text, document)
        self.effective_user = SimpleNamespace(id=42)


def run(awaitable):
    return asyncio.run(awaitable)


def test_production_text_handler_uses_mock_openai_service():
    client = FakeClient()
    config = load_config({"DEMO_MODE": "false", "OPENAI_API_KEY": "test", "REQUIRE_CONFIRMATION_ABOVE_USD": "1"}, dotenv_path=None)
    service = OpenAIService(config, client=client)
    update = FakeUpdate(text="hello")
    run(TelegramHandlers(None, ai_service=service).text(update, None))
    assert len(update.message.replies) == 1
    assert "Загрузите TXT-файл" in update.message.replies[0][0]
    assert "<code>/ask ваш</code> вопрос" in update.message.replies[0][0]
    assert client.responses.calls == []


def test_production_document_handler_uses_mock_openai_service():
    client = FakeClient()
    config = load_config({"DEMO_MODE": "false", "OPENAI_API_KEY": "test", "REQUIRE_CONFIRMATION_ABOVE_USD": "1"}, dotenv_path=None)
    service = OpenAIService(config, client=client)
    document = SimpleNamespace(file_name="notes.txt", file_id="id", file_size=5)
    update = FakeUpdate(document=document)

    class File:
        async def download_as_bytearray(self):
            return bytearray(b"hello")

    class Bot:
        async def get_file(self, file_id):
            return File()

    context = SimpleNamespace(bot=Bot())
    run(TelegramHandlers(None, ai_service=service).document(update, context))
    assert update.message.replies[0][0] == "⏳ Анализирую документ…"
    assert "mocked production answer" in update.message.replies[-2][0]
    assert "По этому документу можно спросить:" in update.message.replies[-1][0]
    assert update.message.sent_messages[0].deleted is True
    assert client.responses.calls[0]["model"] == Model.LUNA.value
