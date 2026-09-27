"""Transport-independent assistant models."""

from dataclasses import dataclass
from enum import Enum


class Command(str, Enum):
    START = "/start"
    HELP = "/help"


@dataclass(frozen=True)
class AssistantResponse:
    text: str
    is_error: bool = False
