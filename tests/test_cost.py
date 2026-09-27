from orchestrator.cost import estimate_task
from orchestrator.models import Task, TaskKind


def test_estimate_is_local_and_deterministic():
    estimate = estimate_task(Task("check", TaskKind.TESTS, 2500, 3))
    assert estimate.tokens == 2500
    assert estimate.operation_count == 3
    assert not estimate.expensive
    assert not estimate.mass_operation
