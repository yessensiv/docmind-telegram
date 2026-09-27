"""In-memory per-user storage for one active TXT document."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class StoredDocument:
    user_id: str
    filename: str
    text: str
    expires_at: datetime


class DocumentStore:
    def __init__(self, ttl_seconds: int = 1800):
        if ttl_seconds < 1:
            raise ValueError("Document TTL must be positive")
        self.ttl = timedelta(seconds=ttl_seconds)
        self._documents: dict[str, StoredDocument] = {}

    def save(self, user_id: str, filename: str, text: str, *, now: datetime | None = None) -> StoredDocument:
        current = now or datetime.now(timezone.utc)
        document = StoredDocument(user_id, filename, text, current + self.ttl)
        self._documents[user_id] = document
        return document

    def get(self, user_id: str, *, now: datetime | None = None) -> StoredDocument | None:
        current = now or datetime.now(timezone.utc)
        document = self._documents.get(user_id)
        if document is None:
            return None
        if current > document.expires_at:
            self._documents.pop(user_id, None)
            return None
        return document

    def delete(self, user_id: str) -> bool:
        return self._documents.pop(user_id, None) is not None

    def has_document(self, user_id: str, *, now: datetime | None = None) -> bool:
        return self.get(user_id, now=now) is not None

    def clear_expired(self, *, now: datetime | None = None) -> int:
        current = now or datetime.now(timezone.utc)
        expired = [user_id for user_id, document in self._documents.items() if current > document.expires_at]
        for user_id in expired:
            self._documents.pop(user_id, None)
        return len(expired)
