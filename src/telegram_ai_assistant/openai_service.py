"""OpenAI Responses API boundary with production safeguards."""

from dataclasses import dataclass
import logging

from orchestrator.models import Model, TaskKind

from .budget import BudgetExceededError, InMemoryBudget
from .config import AssistantConfig, ConfigError
from .confirmation import ConfirmationStore
from .cost_estimator import CostEstimate, estimate_cost
from .model_policy import choose_model


class ConfirmationRequiredError(RuntimeError):
    """Raised before an expensive request until the user confirms it."""


@dataclass(frozen=True)
class ServiceResult:
    text: str
    model: Model
    estimate: CostEstimate


class OpenAIService:
    def __init__(self, config: AssistantConfig, *, budget: InMemoryBudget | None = None,
                 confirmations: ConfirmationStore | None = None, client=None, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger("telegram_ai_assistant.openai_service")
        self.budget = budget or InMemoryBudget(config.daily_budget_usd, config.max_request_cost_usd)
        self.confirmations = confirmations or ConfirmationStore()
        self.client = client
        if config.demo_mode:
            return
        if not config.openai_api_key:
            raise ConfigError("OPENAI_API_KEY is required when DEMO_MODE=false")
        if self.client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError("The official openai package is required in production mode") from exc
            self.client = OpenAI(api_key=config.openai_api_key, timeout=config.openai_timeout_seconds)

    def complete(self, user_id: str, prompt: str, kind: TaskKind, *, confirmed: bool = False) -> ServiceResult:
        if self.config.demo_mode:
            raise ConfigError("OpenAIService is disabled in DEMO_MODE=true")
        decision = choose_model(kind)
        estimate = self._estimate(decision.model, prompt)
        if len(prompt) > self.config.max_message_length:
            return ServiceResult("Сообщение слишком длинное.", decision.model, estimate)
        if estimate.estimated_usd >= self.config.require_confirmation_above_usd:
            if not confirmed or not self.confirmations.consume(user_id, prompt, decision.model):
                self.confirmations.issue(user_id, prompt, decision.model)
                raise ConfirmationRequiredError("Для этого запроса требуется подтверждение.")
        try:
            self.budget.reserve(estimate.estimated_usd)
        except BudgetExceededError:
            return ServiceResult("Лимит расходов исчерпан. Попробуйте позже.", decision.model, estimate)
        try:
            response = self.client.responses.create(
                model=decision.model.value,
                input=prompt[: self.config.max_message_length],
                max_output_tokens=self.config.max_output_tokens,
            )
            text = str(getattr(response, "output_text", "")).strip()
            if not text:
                return ServiceResult("Модель не вернула ответ.", decision.model, estimate)
            return ServiceResult(text[: self.config.max_output_tokens * 4], decision.model, estimate)
        except Exception as exc:
            self.logger.warning("OpenAI request failed: %s", type(exc).__name__)
            return ServiceResult(self._safe_message(exc), decision.model, estimate)

    def _estimate(self, model: Model, prompt: str) -> CostEstimate:
        input_tokens = min(max(1, len(prompt) // 4), self.config.max_input_tokens)
        return estimate_cost(model, input_tokens, self.config.max_output_tokens)

    @staticmethod
    def _safe_message(error: Exception) -> str:
        status = getattr(error, "status_code", getattr(error, "status", None))
        name = type(error).__name__.lower()
        if status == 401 or "authentication" in name:
            return "Ошибка авторизации AI-сервиса."
        if status == 429 or "ratelimit" in name:
            return "AI-сервис временно перегружен. Попробуйте позже."
        if status is not None and int(status) >= 500:
            return "AI-сервис временно недоступен. Попробуйте позже."
        if "timeout" in name or "connection" in name:
            return "Не удалось связаться с AI-сервисом. Попробуйте позже."
        return "Не удалось обработать запрос. Попробуйте позже."
