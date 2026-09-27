"""Optional python-telegram-bot adapter for DEMO_MODE."""

from .config import AssistantConfig, ConfigError
from .handlers import AssistantHandlers
from .telegram_handlers import TelegramHandlers

COMMAND_MENU = (
    ("start", "Запустить ассистента"),
    ("help", "Показать справку"),
    ("ask", "Задать вопрос по TXT-документу"),
    ("clear", "Удалить свой документ"),
    ("status", "Показать безопасный статус"),
)


async def register_commands(bot, command_type=None) -> None:
    if command_type is None:
        from telegram import BotCommand

        command_type = BotCommand
    await bot.set_my_commands([command_type(command, description) for command, description in COMMAND_MENU])


def create_application(config: AssistantConfig, handlers: AssistantHandlers | None = None, ai_service=None):
    if not config.telegram_bot_token:
        raise ConfigError("TELEGRAM_BOT_TOKEN is required to connect the Telegram bot")
    if not config.demo_mode and ai_service is None:
        raise ConfigError("Production Telegram adapter requires OpenAIService")

    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
    except ImportError as exc:
        raise RuntimeError("python-telegram-bot is required to create the Telegram adapter") from exc

    local_handlers = handlers if config.demo_mode else None
    if config.demo_mode and local_handlers is None:
        local_handlers = AssistantHandlers(config)
    telegram_handlers = TelegramHandlers(local_handlers, ai_service=ai_service)

    async def post_init(application):
        await register_commands(application.bot)

    application = Application.builder().token(config.telegram_bot_token).post_init(post_init).build()
    application.add_handler(CommandHandler("start", telegram_handlers.start))
    application.add_handler(CommandHandler("help", telegram_handlers.help))
    application.add_handler(CommandHandler("ask", telegram_handlers.ask))
    application.add_handler(CommandHandler("clear", telegram_handlers.clear))
    application.add_handler(CommandHandler("status", telegram_handlers.status))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_handlers.text))
    application.add_handler(MessageHandler(filters.Document.ALL, telegram_handlers.document))
    return application
