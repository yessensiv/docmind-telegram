from types import SimpleNamespace

import pytest

from orchestrator.models import Model, TaskKind
from telegram_ai_assistant.budget import InMemoryBudget
from telegram_ai_assistant.config import ConfigError, load_config
from telegram_ai_assistant.confirmation import ConfirmationStore
from telegram_ai_assistant.openai_service import ConfirmationRequiredError, OpenAIService


class FakeResponses:
    def __init__(self, output="ok", error=None):
        self.output = output
        self.error = error
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return SimpleNamespace(output_text=self.output)


class FakeClient:
    def __init__(self, responses):
        self.responses = responses


def production_config(**overrides):
    values = {"DEMO_MODE": "false", "OPENAI_API_KEY": "test-key", "REQUIRE_CONFIRMATION_ABOVE_USD": "1.0"}
    values.update(overrides)
    return load_config(values, dotenv_path=None)


def test_demo_mode_does_not_create_client_or_require_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    service = OpenAIService(load_config({"DEMO_MODE": "true"}, dotenv_path=None))
    assert service.client is None


def test_production_uses_responses_api_and_policy_model():
    responses = FakeResponses("answer")
    service = OpenAIService(production_config(), client=FakeClient(responses))
    result = service.complete("user-1", "hello", TaskKind.SIMPLE)
    assert result.model is Model.LUNA
    assert result.text == "answer"
    assert responses.calls[0]["model"] == "gpt-6-luna"
    assert responses.calls[0]["max_output_tokens"] == 500


def test_expensive_request_requires_confirmation_before_client_call():
    responses = FakeResponses()
    service = OpenAIService(
        production_config(REQUIRE_CONFIRMATION_ABOVE_USD="0.00001"),
        client=FakeClient(responses),
        confirmations=ConfirmationStore(),
    )
    with pytest.raises(ConfirmationRequiredError):
        service.complete("user-1", "hello", TaskKind.SIMPLE)
    assert responses.calls == []


def test_api_error_becomes_safe_message_without_secret():
    error = RuntimeError("secret prompt and key")
    error.status_code = 401
    service = OpenAIService(production_config(), client=FakeClient(FakeResponses(error=error)))
    result = service.complete("user-1", "hello", TaskKind.SIMPLE)
    assert result.text == "Ошибка авторизации AI-сервиса."
    assert "secret" not in result.text


def test_production_requires_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        load_config({"DEMO_MODE": "false"}, dotenv_path=None)
