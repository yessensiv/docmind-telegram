"""Async Telegram handlers without a hard import dependency on Telegram."""

import logging

from .errors import MessageTooLongError
from .document_handlers import DocumentHandlers, build_document_analysis_prompt
from .document_limits import MAX_DOCUMENT_BYTES
from .document_service import DocumentError, extract_txt
from .document_store import DocumentStore
from .handlers import AssistantHandlers
from .question_service import QuestionError, QuestionService
from .html_formatter import format_html, split_html
from .budget import InMemoryBudget
from .status_service import StatusService
from .suggested_questions import generate_questions
from .demo_responses import CHAT_HINT, HELP_RESPONSE, START_RESPONSE, demo_reply
from .models import Command
from orchestrator.models import TaskKind


class TelegramHandlers:
    def __init__(self, handlers: AssistantHandlers | None, document_handlers: DocumentHandlers | None = None, ai_service=None, document_store: DocumentStore | None = None, logger: logging.Logger | None = None):
        self.handlers = handlers
        self.document_handlers = document_handlers or DocumentHandlers()
        self.ai_service = ai_service
        self.documents = document_store or DocumentStore()
        config = handlers.config if handlers is not None else ai_service.config
        self.questions = QuestionService(config, self.documents, ai_service)
        budget = ai_service.budget if ai_service is not None else InMemoryBudget(config.daily_budget_usd, config.max_request_cost_usd)
        self.status_service = StatusService(config, self.documents, budget)
        self.logger = logger or logging.getLogger("telegram_ai_assistant.telegram_handlers")

    async def start(self, update, context) -> None:
        await self._reply(update, START_RESPONSE)

    async def help(self, update, context) -> None:
        await self._reply(update, HELP_RESPONSE)

    async def text(self, update, context) -> None:
        incoming_text = getattr(getattr(update, "message", None), "text", None) or ""
        config = self.handlers.config if self.handlers is not None else self.ai_service.config
        if len(incoming_text) > config.max_message_length:
            await self._reply(update, "Сообщение слишком длинное. Сократите его и попробуйте снова.")
            return
        await self._reply(update, "Загрузите TXT-файл или используйте /ask ваш вопрос")

    async def chat(self, update, context) -> None:
        raw = getattr(getattr(update, "message", None), "text", "") or ""
        parts = raw.split(maxsplit=1)
        prompt = parts[1].strip() if len(parts) == 2 else ""
        if not prompt:
            await self._reply(update, CHAT_HINT)
            return
        progress = None
        try:
            if self.ai_service is None:
                response = demo_reply(prompt).text
            else:
                progress = await self._progress(update, "⏳ Обрабатываю запрос…")
                response = self.ai_service.complete(self._user_id(update), prompt, TaskKind.CHAT).text
        except MessageTooLongError:
            await self._reply(update, "Сообщение слишком длинное. Сократите его и попробуйте снова.")
            return
        except Exception:
            self.logger.exception("Unhandled chat error")
            await self._reply(update, "Не удалось обработать запрос. Попробуйте позже.")
            return
        await self._delete_message(progress)
        await self._reply(update, response)

    async def document(self, update, context) -> None:
        document = getattr(getattr(update, "message", None), "document", None)
        if document is None:
            await self._reply(update, "Не удалось получить документ.")
            return
        filename = getattr(document, "file_name", "") or ""
        file_size = getattr(document, "file_size", None)
        if not filename.lower().endswith(".txt"):
            await self._reply(update, "Поддерживаются только TXT-файлы.")
            return
        if file_size is not None and file_size > MAX_DOCUMENT_BYTES:
            await self._reply(update, "Файл слишком большой.")
            return
        progress = None
        try:
            if self.ai_service is not None:
                progress = await self._progress(update, "⏳ Анализирую документ…")
            telegram_file = await context.bot.get_file(document.file_id)
            content = bytes(await telegram_file.download_as_bytearray())
            if self.ai_service is None:
                response = self.document_handlers.analyze(filename, content, file_size)
                text = extract_txt(filename, content)
            else:
                text = extract_txt(filename, content)
                prompt = build_document_analysis_prompt(text)
                response = self.ai_service.complete(self._user_id(update), prompt, TaskKind.DOCUMENTATION).text
            self.documents.save(self._user_id(update), filename, text)
            questions = generate_questions(text)
            response = (
                f"{response}\n\n"
                f"📄 Размер документа: {len(content)} байт\n"
                f"🔤 Символов: {len(text)}"
            )
        except DocumentError as exc:
            await self._reply(update, str(exc))
            return
        except Exception:
            self.logger.exception("Unhandled local document error")
            await self._reply(update, "Не удалось обработать документ. Попробуйте позже.")
            return
        await self._delete_message(progress)
        await self._reply(update, response)
        await self._reply(update, self._format_suggested_questions(questions))

    async def ask(self, update, context) -> None:
        raw = getattr(getattr(update, "message", None), "text", "") or ""
        parts = raw.split(maxsplit=1)
        question = parts[1] if len(parts) == 2 else ""
        progress = None
        try:
            if self.ai_service is not None:
                progress = await self._progress(update, "⏳ Ищу ответ в документе…")
            response = self.questions.ask(self._user_id(update), question)
        except QuestionError as exc:
            await self._reply(update, str(exc))
            return
        await self._delete_message(progress)
        await self._reply(update, response.text)

    async def clear(self, update, context) -> None:
        user_id = self._user_id(update)
        deleted = self.documents.delete(user_id)
        if self.ai_service is not None:
            self.ai_service.confirmations.clear_user(user_id)
        await self._reply(update, "Документ удалён." if deleted else "Активный документ не найден.")

    async def status(self, update, context) -> None:
        await self._reply(update, self.status_service.render(self._user_id(update)))

    @staticmethod
    def _format_suggested_questions(questions) -> str:
        lines = ["По этому документу можно спросить:"]
        lines.extend(f"{index}. {question}" for index, question in enumerate(questions, start=1))
        lines.append("Чтобы задать вопрос, используй /ask ваш вопрос")
        return "\n".join(lines)

    @staticmethod
    async def _reply(update, text: str) -> None:
        message = getattr(update, "message", None)
        if message is not None:
            for chunk in split_html(format_html(text)):
                try:
                    await message.reply_text(chunk, parse_mode="HTML")
                except TypeError:
                    await message.reply_text(chunk)

    @staticmethod
    async def _progress(update, text):
        message = getattr(update, "message", None)
        if message is None:
            return None
        try:
            return await message.reply_text(text, parse_mode="HTML")
        except TypeError:
            return await message.reply_text(text)

    @staticmethod
    async def _delete_message(message) -> None:
        if message is not None and hasattr(message, "delete"):
            await message.delete()

    @staticmethod
    def _user_id(update) -> str:
        user = getattr(update, "effective_user", None)
        if user is None:
            user = getattr(getattr(update, "callback_query", None), "from_user", None)
        return str(getattr(user, "id", "anonymous"))
