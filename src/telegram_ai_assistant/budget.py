"""Single-process in-memory budget guard."""

from dataclasses import dataclass, field
from datetime import date


class BudgetExceededError(ValueError):
    """Raised when a request would exceed a configured budget."""


@dataclass(frozen=True)
class BudgetStatus:
    spent_usd: float
    daily_limit_usd: float
    remaining_usd: float


@dataclass
class InMemoryBudget:
    daily_limit_usd: float
    request_limit_usd: float
    spent_usd: float = 0.0
    day: date = field(default_factory=date.today)

    def __post_init__(self) -> None:
        if self.daily_limit_usd < 0 or self.request_limit_usd < 0:
            raise ValueError("Budget limits must be non-negative")

    def _reset_if_new_day(self, today: date) -> None:
        if today != self.day:
            self.day = today
            self.spent_usd = 0.0

    def reserve(self, estimated_usd: float, *, today: date | None = None) -> None:
        if estimated_usd < 0:
            raise ValueError("Estimated cost must be non-negative")
        current_day = today or date.today()
        self._reset_if_new_day(current_day)
        if estimated_usd > self.request_limit_usd:
            raise BudgetExceededError("Request cost limit exceeded")
        if self.spent_usd + estimated_usd > self.daily_limit_usd:
            raise BudgetExceededError("Daily budget exceeded")
        self.spent_usd += estimated_usd

    def status(self, *, today: date | None = None) -> BudgetStatus:
        current_day = today or date.today()
        self._reset_if_new_day(current_day)
        return BudgetStatus(self.spent_usd, self.daily_limit_usd, max(0.0, self.daily_limit_usd - self.spent_usd))
