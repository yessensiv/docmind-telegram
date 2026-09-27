"""Simple local cost/risk estimates; no provider pricing is queried."""

from dataclasses import dataclass

from .models import Task


@dataclass(frozen=True)
class Estimate:
    tokens: int
    operation_count: int
    expensive: bool
    mass_operation: bool


def estimate_task(task: Task) -> Estimate:
    return Estimate(
        tokens=task.estimated_tokens,
        operation_count=task.operation_count,
        expensive=task.estimated_tokens >= 10_000,
        mass_operation=task.operation_count >= 20,
    )
