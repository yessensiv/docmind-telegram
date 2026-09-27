from datetime import date, datetime, timedelta, timezone

import pytest

from orchestrator.models import Model, TaskKind
from telegram_ai_assistant.budget import BudgetExceededError, InMemoryBudget
from telegram_ai_assistant.confirmation import ConfirmationStore
from telegram_ai_assistant.cost_estimator import estimate_cost
from telegram_ai_assistant.model_policy import choose_model
from telegram_ai_assistant.pricing import ModelTariff


def test_model_policy_defaults_to_luna_and_escalates_by_kind():
    assert choose_model(TaskKind.SIMPLE).model is Model.LUNA
    assert choose_model(TaskKind.DEVELOPMENT).model is Model.SOL
    assert choose_model(TaskKind.ARCHITECTURE).model is Model.ASTRA


def test_cost_estimator_uses_external_tariffs():
    tariffs = {"gpt-6-luna": ModelTariff(1.0, 2.0)}
    estimate = estimate_cost(Model.LUNA, 1000, 500, tariffs)
    assert estimate.estimated_usd == pytest.approx(0.002)


def test_budget_enforces_request_and_daily_limits():
    request_budget = InMemoryBudget(daily_limit_usd=1.00, request_limit_usd=0.006)
    with pytest.raises(BudgetExceededError, match="Request"):
        request_budget.reserve(0.0061, today=date(2026, 1, 1))

    daily_budget = InMemoryBudget(daily_limit_usd=0.01, request_limit_usd=1.00)
    daily_budget.reserve(0.006, today=date(2026, 1, 1))
    with pytest.raises(BudgetExceededError, match="Daily"):
        daily_budget.reserve(0.005, today=date(2026, 1, 1))


def test_budget_resets_on_new_day():
    budget = InMemoryBudget(daily_limit_usd=0.01, request_limit_usd=0.01)
    budget.reserve(0.01, today=date(2026, 1, 1))
    budget.reserve(0.01, today=date(2026, 1, 2))
    assert budget.spent_usd == pytest.approx(0.01)


def test_confirmation_is_bound_to_user_query_model_and_ttl():
    store = ConfirmationStore(ttl_seconds=60)
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    store.issue("user-1", "private query", Model.SOL, now=now)
    assert store.consume("user-1", "private query", Model.SOL, now=now + timedelta(seconds=30))
    assert not store.consume("user-1", "private query", Model.SOL, now=now + timedelta(seconds=30))


def test_expired_or_mismatched_confirmation_is_rejected():
    store = ConfirmationStore(ttl_seconds=60)
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    store.issue("user-1", "query", Model.ASTRA, now=now)
    assert not store.consume("user-2", "query", Model.ASTRA, now=now)
    store.issue("user-1", "query", Model.ASTRA, now=now)
    assert not store.consume("user-1", "other", Model.ASTRA, now=now)
    store.issue("user-1", "query", Model.ASTRA, now=now)
    assert not store.consume("user-1", "query", Model.ASTRA, now=now + timedelta(seconds=61))
