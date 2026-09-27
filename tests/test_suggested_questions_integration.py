import asyncio
from types import SimpleNamespace

from telegram_ai_assistant.config import load_config
from telegram_ai_assistant.document_store import DocumentStore
from telegram_ai_assistant.handlers import AssistantHandlers
from telegram_ai_assistant.telegram_handlers import TelegramHandlers


class Message:
    def __init__(self, document=None):
        self.document = document
        self.text = None
        self.replies = []

    async def reply_text(self, text, reply_markup=None, parse_mode=None):
        self.replies.append((text, reply_markup, parse_mode))


class Update:
    def __init__(self, user_id, document):
        self.effective_user = SimpleNamespace(id=user_id)
        self.message = Message(document)


def test_document_upload_sends_five_questions_as_plain_text():
    config = load_config({"DEMO_MODE": "true"}, dotenv_path=None)
    document = SimpleNamespace(file_name="notes.txt", file_id="id", file_size=5)
    update = Update("one", document)

    class File:
        async def download_as_bytearray(self):
            return bytearray(b"Status is complete")

    class Bot:
        async def get_file(self, file_id):
            return File()

    handlers = TelegramHandlers(AssistantHandlers(config), document_store=DocumentStore())
    asyncio.run(handlers.document(update, SimpleNamespace(bot=Bot())))
    questions = update.message.replies[1][0]
    assert "<b>По этому документу можно спросить:</b>" in questions
    assert sum(questions.count(f"{index}. ") for index in range(1, 6)) == 5
    assert "<code>/ask ваш</code> вопрос" in questions
    assert all(markup is None for _, markup, _ in update.message.replies)
