from orchestrator.models import Model, Task, TaskKind
from orchestrator.router import route_task


def test_architecture_uses_astra():
    route = route_task(Task("design system", TaskKind.ARCHITECTURE))
    assert route.model is Model.ASTRA


def test_development_uses_sol():
    route = route_task(Task("implement feature", TaskKind.DEVELOPMENT))
    assert route.model is Model.SOL


def test_simple_work_uses_luna():
    route = route_task(Task("write docs", TaskKind.DOCUMENTATION))
    assert route.model is Model.LUNA


def test_expensive_operation_requires_confirmation():
    route = route_task(Task("large task", TaskKind.DEVELOPMENT, estimated_tokens=10_000))
    assert route.requires_confirmation is True
    assert "Confirmation" in route.reason


def test_confirmation_allows_expensive_operation():
    route = route_task(
        Task("large task", TaskKind.DEVELOPMENT, estimated_tokens=10_000),
        confirmed=True,
    )
    assert route.requires_confirmation is True
    assert route.model is Model.SOL


def test_mass_operation_requires_confirmation():
    route = route_task(Task("batch", TaskKind.TESTS, operation_count=20))
    assert route.requires_confirmation is True
