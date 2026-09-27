import pytest

from telegram_ai_assistant.ai_service import AiService
from telegram_ai_assistant.config import AssistantConfig, ConfigError, load_config
from telegram_ai_assistant.demo_responses import HELP_RESPONSE, START_RESPONSE
from telegram_ai_assistant.errors import MessageTooLongError
from telegram_ai_assistant.handlers import AssistantHandlers


@pytest.fixture
def handlers():
    return AssistantHandlers(load_config({"DEMO_MODE": "true", "MAX_MESSAGE_LENGTH": "20"}, dotenv_path=None))


@pytest.fixture
def command_handlers():
    return AssistantHandlers(load_config({"DEMO_MODE": "true", "MAX_MESSAGE_LENGTH": "100"}, dotenv_path=None))


def test_start(handlers):
    assert handlers.handle("/start").text == START_RESPONSE


def test_help(handlers):
    assert handlers.handle("/help").text == HELP_RESPONSE


def test_commands_allow_surrounding_spaces_and_arguments(command_handlers):
    assert command_handlers.handle("  /start  привет").text == START_RESPONSE
    assert command_handlers.handle("\t/help additional text").text == HELP_RESPONSE


def test_demo_text_reply(handlers):
    response = handlers.handle("Привет")
    assert response.is_error is False
    assert "Демо-ответ" in response.text


def test_message_at_limit_is_accepted(handlers):
    response = handlers.handle("x" * 20)
    assert response.is_error is False
    assert "20" in response.text


def test_message_over_limit_is_rejected(handlers):
    with pytest.raises(MessageTooLongError):
        handlers.handle("x" * 21)


def test_empty_message_is_safe_error(handlers):
    response = handlers.handle(None)
    assert response.is_error is True


def test_ai_service_rejects_non_demo_config():
    with pytest.raises(ConfigError):
        AiService(AssistantConfig(demo_mode=False))
