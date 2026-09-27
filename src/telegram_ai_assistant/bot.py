"""Bot facades for local demo handling and optional Telegram integration."""

from .config import AssistantConfig
from .handlers import AssistantHandlers
from .telegram_adapter import create_application


class DemoBot:
    def __init__(self, config: AssistantConfig):
        self.handlers = AssistantHandlers(config)

    def handle_text(self, text: str):
        return self.handlers.handle(text)


def create_telegram_bot(config: AssistantConfig):
    return create_application(config)
