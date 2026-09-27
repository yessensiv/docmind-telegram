"""Deterministic task routing with confirmation safeguards."""

from dataclasses import dataclass

from .config import ASTRA_TOKEN_THRESHOLD, MASS_OPERATION_THRESHOLD, MODEL_BY_KIND
from .cost import estimate_task
from .models import Model, Task


@dataclass(frozen=True)
class Route:
    model: Model
    estimated_tokens: int
    requires_confirmation: bool
    reason: str


def route_task(task: Task, *, confirmed: bool = False) -> Route:
    estimate = estimate_task(task)
    model = MODEL_BY_KIND[task.kind]
    expensive = estimate.tokens >= ASTRA_TOKEN_THRESHOLD
    mass_operation = estimate.operation_count >= MASS_OPERATION_THRESHOLD
    needs_confirmation = task.requires_confirmation or expensive or mass_operation

    if needs_confirmation and not confirmed:
        reason = "Confirmation required for an expensive or mass operation"
    elif model is Model.ASTRA:
        reason = "Architecture or final-review work"
    elif model is Model.SOL:
        reason = "Development or complex bug-fix work"
    else:
        reason = "Simple, testing, documentation, or template work"

    return Route(model, estimate.tokens, needs_confirmation, reason)
