"""Short-lived confirmation records for expensive requests."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib

from orchestrator.models import Model


@dataclass(frozen=True)
class Confirmation:
    user_id: str
    query_hash: str
    model: Model
    expires_at: datetime


class ConfirmationStore:
    def __init__(self, ttl_seconds: int = 300):
        if ttl_seconds < 1:
            raise ValueError("TTL must be positive")
        self.ttl = timedelta(seconds=ttl_seconds)
        self._items: dict[tuple[str, str, Model], Confirmation] = {}

    @staticmethod
    def hash_query(query: str) -> str:
        return hashlib.sha256(query.encode("utf-8")).hexdigest()

    def issue(self, user_id: str, query: str, model: Model, *, now: datetime | None = None) -> Confirmation:
        current = now or datetime.now(timezone.utc)
        confirmation = Confirmation(user_id, self.hash_query(query), model, current + self.ttl)
        self._items[(user_id, confirmation.query_hash, model)] = confirmation
        return confirmation

    def consume(self, user_id: str, query: str, model: Model, *, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        key = (user_id, self.hash_query(query), model)
        confirmation = self._items.pop(key, None)
        return confirmation is not None and current <= confirmation.expires_at

    def clear_user(self, user_id: str) -> int:
        keys = [key for key in self._items if key[0] == user_id]
        for key in keys:
            self._items.pop(key, None)
        return len(keys)
