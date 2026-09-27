"""Transport-independent handlers for Telegram-style messages."""

import logging

from .ai_service import AiService
from .config import AssistantConfig
from .demo_responses import HELP_RESPONSE, START_RESPONSE
from .errors import MessageTooLongError
from .models import AssistantResponse, Command


class AssistantHandlers:
    def __init__(self, config: AssistantConfig, ai_service: AiService | None = None, logger: logging.Logger | None = None):
        self.config = config
        self.ai_service = ai_service or AiService(config)
        self.logger = logger or logging.getLogger("telegram_ai_assistant.handlers")

    def handle(self, text: str | None) -> AssistantResponse:
        normalized_text = text or ""
        if len(normalized_text) > self.config.max_message_length:
            self.logger.warning("Rejected message exceeding configured length limit")
            raise MessageTooLongError("Сообщение слишком длинное")
        command = normalized_text.strip().split(maxsplit=1)[0] if normalized_text.strip() else ""
        if command == Command.START.value:
            return AssistantResponse(START_RESPONSE)
        if command == Command.HELP.value:
            return AssistantResponse(HELP_RESPONSE)
        if not normalized_text.strip():
            return AssistantResponse("Пожалуйста, отправьте текстовое сообщение.", is_error=True)
        return self.ai_service.reply(normalized_text)
