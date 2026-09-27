"""Environment configuration for the assistant."""

from dataclasses import dataclass
import os
from pathlib import Path


class ConfigError(ValueError):
    """Raised when assistant configuration is invalid."""


@dataclass(frozen=True)
class AssistantConfig:
    demo_mode: bool
    max_message_length: int = 4000
    log_level: str = "INFO"
    telegram_bot_token: str | None = None
    default_model: str = "gpt-6-luna"
    max_request_cost_usd: float = 0.02
    daily_budget_usd: float = 1.00
    require_confirmation_above_usd: float = 0.01
    openai_api_key: str | None = None
    openai_timeout_seconds: float = 20.0
    max_input_tokens: int = 4000
    max_output_tokens: int = 500
    max_question_length: int = 1000
    max_answer_length: int = 2000
    document_ttl_seconds: int = 1800


def _load_dotenv_values(path: str | Path | None = ".env", *, include_openai_key: bool = False) -> dict[str, str]:
    if path is None:
        return {}
    dotenv_path = Path(path)
    if not dotenv_path.is_file():
        return {}
    values = {}
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        if key == "OPENAI_API_KEY" and not include_openai_key:
            continue
        values[key] = value.strip().strip("\"'")
    return values


def load_config(env: dict[str, str] | None = None, dotenv_path: str | Path | None = ".env") -> AssistantConfig:
    environment = os.environ if env is None else env
    dotenv_values = _load_dotenv_values(dotenv_path)

    def setting(name: str, default: str) -> str:
        if name in environment:
            return environment[name]
        return dotenv_values.get(name, default)

    raw_demo = setting("DEMO_MODE", "true").strip().lower()
    if raw_demo not in {"true", "false"}:
        raise ConfigError("DEMO_MODE must be true or false")
    demo_mode = raw_demo == "true"

    raw_limit = setting("MAX_MESSAGE_LENGTH", "4000").strip()
    try:
        max_length = int(raw_limit)
    except ValueError as exc:
        raise ConfigError("MAX_MESSAGE_LENGTH must be an integer") from exc
    if max_length < 1:
        raise ConfigError("MAX_MESSAGE_LENGTH must be positive")

    log_level = setting("LOG_LEVEL", "INFO").strip().upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ConfigError("LOG_LEVEL is invalid")
    telegram_token = setting("TELEGRAM_BOT_TOKEN", "").strip() or None
    raw_timeout = setting("OPENAI_TIMEOUT_SECONDS", "20").strip()
    try:
        timeout = float(raw_timeout)
    except ValueError as exc:
        raise ConfigError("OPENAI_TIMEOUT_SECONDS must be a number") from exc
    if timeout <= 0:
        raise ConfigError("OPENAI_TIMEOUT_SECONDS must be positive")

    def positive_int(name: str, default: int) -> int:
        raw = setting(name, str(default)).strip()
        try:
            result = int(raw)
        except ValueError as exc:
            raise ConfigError(f"{name} must be an integer") from exc
        if result < 1:
            raise ConfigError(f"{name} must be positive")
        return result

    api_key = None
    if not demo_mode:
        production_dotenv = _load_dotenv_values(dotenv_path, include_openai_key=True)
        api_key = (environment.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in environment else production_dotenv.get("OPENAI_API_KEY"))
        api_key = api_key.strip() if api_key else None
    if not demo_mode and not api_key:
        raise ConfigError("OPENAI_API_KEY is required when DEMO_MODE=false")

    return AssistantConfig(
        demo_mode,
        max_length,
        log_level,
        telegram_token,
        setting("OPENAI_MODEL_DEFAULT", "gpt-6-luna").strip() or "gpt-6-luna",
        _positive_float(setting, "MAX_REQUEST_COST_USD", 0.02),
        _positive_float(setting, "DAILY_BUDGET_USD", 1.00),
        _positive_float(setting, "REQUIRE_CONFIRMATION_ABOVE_USD", 0.01),
        api_key,
        timeout,
        positive_int("MAX_INPUT_TOKENS", 4000),
        positive_int("MAX_OUTPUT_TOKENS", 500),
        positive_int("MAX_QUESTION_LENGTH", 1000),
        positive_int("MAX_ANSWER_LENGTH", 2000),
        positive_int("DOCUMENT_TTL_SECONDS", 1800),
    )


def _positive_float(setting, name: str, default: float) -> float:
    raw = setting(name, str(default)).strip()
    try:
        result = float(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a number") from exc
    if result < 0:
        raise ConfigError(f"{name} must be non-negative")
    return result
