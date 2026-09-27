"""AI service boundary; only local demo behavior is available."""

from .demo_responses import demo_reply
from .config import AssistantConfig, ConfigError
from .models import AssistantResponse


class AiService:
    def __init__(self, config: AssistantConfig):
        if not config.demo_mode:
            raise ConfigError("AiService supports DEMO_MODE=true only")
        self.config = config

    def reply(self, message: str) -> AssistantResponse:
        return demo_reply(message)
