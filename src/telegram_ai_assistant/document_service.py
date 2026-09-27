"""Dependency-free, in-memory TXT analysis."""

from .document_limits import MAX_DOCUMENT_BYTES, MAX_DOCUMENT_CHARACTERS, PREVIEW_LINES
from .document_models import DocumentAnalysis


class DocumentError(ValueError):
    """Safe, user-facing document validation error."""


def analyze_txt(filename: str, content: bytes) -> DocumentAnalysis:
    if not filename.lower().endswith(".txt"):
        raise DocumentError("Поддерживаются только TXT-файлы")
    if len(content) > MAX_DOCUMENT_BYTES:
        raise DocumentError("Файл слишком большой")
    text = extract_txt(filename, content, validate_size=False)
    if len(text) > MAX_DOCUMENT_CHARACTERS:
        raise DocumentError("Текстовый документ слишком длинный")
    if not text.strip():
        raise DocumentError("Документ пуст")

    nonempty_lines = tuple(line.strip() for line in text.splitlines() if line.strip())
    preview = nonempty_lines[:PREVIEW_LINES]
    summary = (
        f"Demo-резюме: {len(text)} символов, {len(text.splitlines())} строк. "
        f"Непустых строк: {len(nonempty_lines)}."
    )
    return DocumentAnalysis(filename, len(text), len(text.splitlines()), preview, summary)


def extract_txt(filename: str, content: bytes, *, validate_size: bool = True) -> str:
    if not filename.lower().endswith(".txt"):
        raise DocumentError("Поддерживаются только TXT-файлы")
    if validate_size and len(content) > MAX_DOCUMENT_BYTES:
        raise DocumentError("Файл слишком большой")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DocumentError("Не удалось прочитать TXT-файл в кодировке UTF-8") from exc
    if len(text) > MAX_DOCUMENT_CHARACTERS:
        raise DocumentError("Текстовый документ слишком длинный")
    if not text.strip():
        raise DocumentError("Документ пуст")
    return text
