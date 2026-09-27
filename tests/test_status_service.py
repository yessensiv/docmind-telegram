from telegram_ai_assistant.budget import InMemoryBudget
from telegram_ai_assistant.config import load_config
from telegram_ai_assistant.document_store import DocumentStore
from telegram_ai_assistant.status_service import StatusService


def test_status_reports_safe_budget_and_document_state():
    config = load_config({"DEMO_MODE": "true", "DAILY_BUDGET_USD": "2"}, dotenv_path=None)
    budget = InMemoryBudget(2.0, 1.0)
    budget.reserve(0.25)
    store = DocumentStore()
    status = StatusService(config, store, budget).render("user-1")
    assert "Использовано за день: $0.2500" in status
    assert "Дневной лимит: $2.0000" in status
    assert "не загружен" in status
