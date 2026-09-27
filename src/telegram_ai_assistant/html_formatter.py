"""Safe Telegram HTML formatting and message splitting."""

from html import escape
import re

TELEGRAM_MESSAGE_LIMIT = 4096


def format_html(text: str) -> str:
    lines = []
    for raw_line in text.splitlines():
        line = escape(raw_line, quote=False)
        for heading, emoji in (
            ("КРАТКОЕ РЕЗЮМЕ:", "📝"),
            ("КЛЮЧЕВЫЕ ПУНКТЫ:", "🔹"),
            ("СТАТУС:", "📌"),
            ("ПО ДОКУМЕНТУ МОЖНО СПРОСИТЬ:", "💡"),
        ):
            if line == heading:
                line = f"{emoji} <b>{heading}</b>"
                break
        if line.endswith(":") and not line.startswith(("•", "-", "*")):
            line = f"<b>{line}</b>"
        line = re.sub(r"(?<!\w)(/(?:start|help|ask|clear|status)(?:\s+[^\s]+)?)", r"<code>\1</code>", line)
        if line.startswith(("- ", "* ")):
            line = "• " + line[2:]
        lines.append(line)
    return "\n".join(lines)


def split_html(text: str, limit: int = TELEGRAM_MESSAGE_LIMIT) -> list[str]:
    if limit < 100:
        raise ValueError("Telegram message limit is too small")
    if len(text) <= limit:
        return [text]
    chunks = []
    current = ""
    for paragraph in text.split("\n\n"):
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= limit:
            current = candidate
        else:
            if current:
                chunks.append(current)
            while len(paragraph) > limit:
                chunks.append(paragraph[:limit])
                paragraph = paragraph[limit:]
            current = paragraph
    if current:
        chunks.append(current)
    return chunks
