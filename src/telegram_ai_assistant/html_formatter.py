"""Safe Telegram HTML formatting and message splitting."""

from html import escape
import re

TELEGRAM_MESSAGE_LIMIT = 4096


def format_html(text: str) -> str:
    lines = []
    for raw_line in text.splitlines():
        preserved: dict[str, str] = {}

        def preserve_tag(match: re.Match[str]) -> str:
            token = f"\x00TAG{len(preserved)}\x00"
            preserved[token] = match.group(0)
            return token

        # Keep only Telegram-safe tags that may already be present in generated text.
        line = re.sub(r"</?(?:b|i|code)>", preserve_tag, raw_line, flags=re.IGNORECASE)
        line = escape(line, quote=False)
        line = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", line)
        line = re.sub(r"\*\*([^*\n]+)\*\*", r"<b>\1</b>", line)
        line = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", line)
        for heading, label, emoji in (
            ("КРАТКОЕ РЕЗЮМЕ:", "РЕЗЮМЕ", "📝"),
            ("КЛЮЧЕВЫЕ ПУНКТЫ:", "ГЛАВНОЕ", "🔹"),
            ("СТАТУС:", "СТАТУС", "📌"),
            ("ПО ДОКУМЕНТУ МОЖНО СПРОСИТЬ:", "ПО ДОКУМЕНТУ МОЖНО СПРОСИТЬ", "💡"),
            ("📄 ИНФОРМАЦИЯ О ФАЙЛЕ:", "ИНФОРМАЦИЯ О ФАЙЛЕ", "📄"),
        ):
            if line == heading:
                line = f"{emoji} <b>{label}</b>"
                break
        if line.endswith(":") and not line.startswith(("•", "-", "*")):
            line = f"<b>{line}</b>"
        line = re.sub(r"(?<!\w)(/(?:start|help|ask|chat|clear|status)(?:\s+[^\s]+)?)", r"<code>\1</code>", line)
        if line.startswith(("- ", "* ")):
            line = "• " + line[2:]
        for token, tag in preserved.items():
            line = line.replace(token, tag)
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
