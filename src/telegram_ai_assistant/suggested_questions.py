"""Local suggested-question generation and per-user in-memory state."""


DEFAULT_QUESTIONS = (
    "Какова основная тема документа?",
    "Какие ключевые факты указаны в документе?",
    "Какой статус указан в документе?",
    "Какие даты или сроки упоминаются?",
    "Какие участники или объекты названы?",
)


def generate_questions(text: str) -> tuple[str, ...]:
    """Return deterministic questions without logging or external calls."""
    if not text.strip():
        return ()
    return DEFAULT_QUESTIONS
