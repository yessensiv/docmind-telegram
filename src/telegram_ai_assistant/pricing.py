"""Model tariffs kept separately from cost calculation logic."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelTariff:
    input_per_million: float
    output_per_million: float


MODEL_TARIFFS = {
    "gpt-6-luna": ModelTariff(input_per_million=0.10, output_per_million=0.50),
    "gpt-6-sol": ModelTariff(input_per_million=2.00, output_per_million=10.00),
    "gpt-6-astra": ModelTariff(input_per_million=10.00, output_per_million=50.00),
}
