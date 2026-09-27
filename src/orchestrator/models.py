"""Core types for the offline orchestrator."""

from dataclasses import dataclass
from enum import Enum


class Model(str, Enum):
    ASTRA = "gpt-6-astra"
    SOL = "gpt-6-sol"
    LUNA = "gpt-6-luna"


class TaskKind(str, Enum):
    ARCHITECTURE = "architecture"
    DEVELOPMENT = "development"
    BUGFIX = "bugfix"
    SIMPLE = "simple"
    TESTS = "tests"
    DOCUMENTATION = "documentation"
    TEMPLATE = "template"


@dataclass(frozen=True)
class Task:
    description: str
    kind: TaskKind
    estimated_tokens: int = 1000
    operation_count: int = 1
    requires_confirmation: bool = False

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("Task description must not be empty")
        if self.estimated_tokens < 0:
            raise ValueError("estimated_tokens must be non-negative")
        if self.operation_count < 1:
            raise ValueError("operation_count must be positive")
