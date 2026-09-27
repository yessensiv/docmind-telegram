"""Deterministic local responses for portfolio/demo usage."""

from .models import AssistantResponse

START_RESPONSE = "👋 Привет! Я AI-ассистент для анализа TXT-документов.\nЗагрузи TXT-файл или отправь /help, чтобы увидеть доступные команды."
HELP_RESPONSE = (
    "🤖 <b>Доступные команды</b>\n\n"
    "/start — запустить ассистента\n"
    "/help — показать справку\n"
    "/chat — Общаться с ИИ без документа\n"
    "/ask <вопрос> — задать вопрос по TXT-документу\n"
    "/clear — удалить текущий документ\n"
    "/status — показать режим и бюджет\n\n"
    "💬 Также можно отправить обычное сообщение."
)

CHAT_HINT = "Использование: /chat <сообщение>"


def demo_reply(message: str) -> AssistantResponse:
    return AssistantResponse(f"Демо-ответ: я получил сообщение длиной {len(message)} символов.")
