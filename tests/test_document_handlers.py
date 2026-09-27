import asyncio

from telegram_ai_assistant.config import load_config
from telegram_ai_assistant.document_handlers import DocumentHandlers
from telegram_ai_assistant.document_service import DocumentError
from telegram_ai_assistant.handlers import AssistantHandlers
from telegram_ai_assistant.telegram_handlers import TelegramHandlers


class FakeMessage:
    def __init__(self, document=None):
        self.document = document
        self.replies = []

    async def reply_text(self, text, reply_markup=None):
        self.replies.append((text, reply_markup))


class FakeUpdate:
    def __init__(self, document=None):
        self.message = FakeMessage(document)


class FakeDocument:
    def __init__(self, filename, content=b"text", size=None):
        self.file_name = filename
        self.file_id = "local-test-id"
        self.file_size = size
        self.content = content


class FakeTelegramFile:
    def __init__(self, content):
        self.content = content

    async def download_as_bytearray(self):
        return bytearray(self.content)


class FakeBot:
    def __init__(self, content):
        self.content = content

    async def get_file(self, file_id):
        return FakeTelegramFile(self.content)


class FakeContext:
    def __init__(self, content):
        self.bot = FakeBot(content)


def run(coroutine):
    return asyncio.run(coroutine)


def test_document_handler_returns_demo_summary():
    document = FakeDocument("notes.txt", b"Title\nBody")
    update = FakeUpdate(document)
    context = FakeContext(document.content)
    handlers = TelegramHandlers(AssistantHandlers(load_config({"DEMO_MODE": "true"}, dotenv_path=None)))
    run(handlers.document(update, context))
    response = update.message.replies[0][0]
    assert "📝 <b>РЕЗЮМЕ</b>" in response
    assert "🔹 <b>ГЛАВНОЕ</b>" in response
    assert "📌 <b>СТАТУС</b>" in response
    assert "📄 <b>ИНФОРМАЦИЯ О ФАЙЛЕ</b>" in response
    assert "Размер: 10 байт" in response
    assert "Символов: 10" in response


def test_document_handler_rejects_pdf_without_download():
    document = FakeDocument("notes.pdf", b"ignored")
    update = FakeUpdate(document)
    context = FakeContext(document.content)
    handlers = TelegramHandlers(AssistantHandlers(load_config({"DEMO_MODE": "true"}, dotenv_path=None)))
    run(handlers.document(update, context))
    assert "только TXT" in update.message.replies[0][0]


def test_document_handlers_keep_errors_safe():
    handler = DocumentHandlers()
    try:
        handler.analyze("bad.docx", b"secret")
    except DocumentError as exc:
        assert "secret" not in str(exc)
    else:
        raise AssertionError("DocumentError was not raised")
