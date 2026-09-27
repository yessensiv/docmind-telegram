"""User-safe assistant errors."""


class MessageTooLongError(ValueError):
    """Raised when a message exceeds the configured limit."""


class AssistantError(RuntimeError):
    """Base error for safe assistant failures."""
