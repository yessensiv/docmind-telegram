"""Deterministic model selection policy for future production calls."""

from dataclasses import dataclass

from orchestrator.models import Model, TaskKind


@dataclass(frozen=True)
class ModelDecision:
    model: Model
    reason: str


def choose_model(kind: TaskKind) -> ModelDecision:
    if kind is TaskKind.ARCHITECTURE:
        return ModelDecision(Model.ASTRA, "architecture or final review")
    if kind in {TaskKind.DEVELOPMENT, TaskKind.BUGFIX}:
        return ModelDecision(Model.SOL, "development or complex bug fix")
    return ModelDecision(Model.LUNA, "simple, test, documentation, or template work")
