"""Local deterministic cost estimation; never calls a provider."""

from dataclasses import dataclass

from orchestrator.models import Model

from .pricing import MODEL_TARIFFS, ModelTariff


@dataclass(frozen=True)
class CostEstimate:
    model: Model
    input_tokens: int
    output_tokens: int
    estimated_usd: float


def estimate_cost(model: Model, input_tokens: int, output_tokens: int, tariffs: dict[str, ModelTariff] | None = None) -> CostEstimate:
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("Token counts must be non-negative")
    tariff_map = tariffs or MODEL_TARIFFS
    try:
        tariff = tariff_map[model.value]
    except KeyError as exc:
        raise ValueError(f"No tariff configured for {model.value}") from exc
    cost = (input_tokens * tariff.input_per_million + output_tokens * tariff.output_per_million) / 1_000_000
    return CostEstimate(model, input_tokens, output_tokens, cost)
