"""Static, offline configuration."""

from .models import Model, TaskKind

MODEL_BY_KIND = {
    TaskKind.ARCHITECTURE: Model.ASTRA,
    TaskKind.DEVELOPMENT: Model.SOL,
    TaskKind.BUGFIX: Model.SOL,
    TaskKind.SIMPLE: Model.LUNA,
    TaskKind.TESTS: Model.LUNA,
    TaskKind.DOCUMENTATION: Model.LUNA,
    TaskKind.TEMPLATE: Model.LUNA,
}

ASTRA_TOKEN_THRESHOLD = 10_000
MASS_OPERATION_THRESHOLD = 20
