"""Models for in-memory TXT document analysis."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentAnalysis:
    filename: str
    characters: int
    lines: int
    preview: tuple[str, ...]
    summary: str
