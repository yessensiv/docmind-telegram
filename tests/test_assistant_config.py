import pytest

from telegram_ai_assistant.config import ConfigError, load_config


def test_demo_mode_is_enabled_by_default():
    config = load_config({"DEMO_MODE": "true"}, dotenv_path=None)
    assert config.demo_mode is True


def test_non_demo_mode_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        load_config({"DEMO_MODE": "false"}, dotenv_path=None)


def test_non_demo_mode_reads_api_key_only_in_production():
    config = load_config({"DEMO_MODE": "false", "OPENAI_API_KEY": "test-key"}, dotenv_path=None)
    assert config.openai_api_key == "test-key"


def test_demo_mode_does_not_read_openai_key_from_dotenv(tmp_path):
    dotenv = tmp_path / ".env"
    dotenv.write_text("DEMO_MODE=true\nOPENAI_API_KEY=must-not-be-read\n", encoding="utf-8")
    config = load_config({"DEMO_MODE": "true"}, dotenv_path=dotenv)
    assert config.demo_mode is True
    assert config.openai_api_key is None


def test_production_mode_can_be_loaded_from_dotenv(tmp_path):
    dotenv = tmp_path / ".env"
    dotenv.write_text("DEMO_MODE=false\nOPENAI_API_KEY=dotenv-key\n", encoding="utf-8")
    config = load_config({}, dotenv_path=dotenv)
    assert config.demo_mode is False
    assert config.openai_api_key == "dotenv-key"


def test_environment_overrides_dotenv(tmp_path):
    dotenv = tmp_path / ".env"
    dotenv.write_text("DEMO_MODE=true\nMAX_MESSAGE_LENGTH=10\n", encoding="utf-8")
    config = load_config({"DEMO_MODE": "false", "OPENAI_API_KEY": "env-key", "MAX_MESSAGE_LENGTH": "20"}, dotenv_path=dotenv)
    assert config.demo_mode is False
    assert config.max_message_length == 20
    assert config.openai_api_key == "env-key"


def test_invalid_limit_is_rejected():
    with pytest.raises(ConfigError):
        load_config({"DEMO_MODE": "true", "MAX_MESSAGE_LENGTH": "zero"}, dotenv_path=None)


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "debug"])
def test_allowed_log_levels(level):
    assert load_config({"DEMO_MODE": "true", "LOG_LEVEL": level}, dotenv_path=None).log_level == level.upper()


def test_invalid_log_level_is_rejected():
    with pytest.raises(ConfigError):
        load_config({"DEMO_MODE": "true", "LOG_LEVEL": "TRACE"}, dotenv_path=None)
