from datetime import datetime, timedelta, timezone

from telegram_ai_assistant.document_store import DocumentStore


def test_store_isolated_and_replaces_document():
    store = DocumentStore()
    store.save("one", "a.txt", "first")
    store.save("one", "b.txt", "second")
    store.save("two", "c.txt", "other")
    assert store.get("one").text == "second"
    assert store.get("two").text == "other"
    assert store.get("missing") is None


def test_store_ttl_and_cleanup():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    store = DocumentStore(ttl_seconds=1800)
    store.save("one", "a.txt", "text", now=now)
    assert store.get("one", now=now + timedelta(seconds=1801)) is None
    assert store.clear_expired(now=now + timedelta(seconds=1801)) == 0
