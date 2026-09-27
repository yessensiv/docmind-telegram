"""Configuration entry point for the offline demo."""

from .config import load_config
from .logging_config import configure_logging
from .telegram_adapter import create_application
from .openai_service import OpenAIService
from .ai_service import AiService
from .handlers import AssistantHandlers


def create_demo_bot():
    config = load_config()
    configure_logging(config.log_level)
    from .bot import DemoBot

    return DemoBot(config)


def create_telegram_app(config=None):
    config = config or load_config()
    configure_logging(config.log_level)
    if config.demo_mode:
        local_service = AiService(config)
        return create_application(config, handlers=AssistantHandlers(config, ai_service=local_service))
    return create_application(config, ai_service=OpenAIService(config))


def main():
    config = load_config()
    application = create_telegram_app(config)
    application.run_polling()


if __name__ == "__main__":
    main()
