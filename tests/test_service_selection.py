from types import SimpleNamespace

from telegram_ai_assistant.ai_service import AiService
from telegram_ai_assistant.config import load_config
from telegram_ai_assistant.main import create_telegram_app
from telegram_ai_assistant.openai_service import OpenAIService


def test_demo_and_production_create_different_services(monkeypatch):
    captured = []
    monkeypatch.setattr("telegram_ai_assistant.main.configure_logging", lambda level: None)
    monkeypatch.setattr("telegram_ai_assistant.main.create_application", lambda config, handlers=None, ai_service=None: captured.append((handlers, ai_service)) or SimpleNamespace())
    monkeypatch.setattr("telegram_ai_assistant.main.OpenAIService", lambda config: "production-service")

    create_telegram_app(load_config({"DEMO_MODE": "true", "TELEGRAM_BOT_TOKEN": "demo"}, dotenv_path="missing.env"))
    create_telegram_app(load_config({"DEMO_MODE": "false", "TELEGRAM_BOT_TOKEN": "prod", "OPENAI_API_KEY": "key"}, dotenv_path="missing.env"))

    assert isinstance(captured[0][0].ai_service, AiService)
    assert captured[0][1] is None
    assert captured[1][0] is None
    assert captured[1][1] == "production-service"
