"""Safe, user-facing status formatting."""

from .budget import InMemoryBudget
from .config import AssistantConfig
from .document_store import DocumentStore


class StatusService:
    def __init__(self, config: AssistantConfig, documents: DocumentStore, budget: InMemoryBudget):
        self.config = config
        self.documents = documents
        self.budget = budget

    def render(self, user_id: str) -> str:
        mode = "DEMO_MODE" if self.config.demo_mode else "production"
        document_state = "загружен" if self.documents.has_document(user_id) else "не загружен"
        budget = self.budget.status()
        return (
            f"⚙️ <b>Статус ассистента</b>\n\n"
            f"Режим: {mode}\n"
            f"Модель по умолчанию: <code>{self.config.default_model}</code>\n"
            f"Документ: {document_state}\n"
            f"Использовано за день: ${budget.spent_usd:.4f}\n"
            f"Дневной лимит: ${budget.daily_limit_usd:.4f}"
        )
