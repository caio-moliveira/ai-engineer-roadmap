"""Tabela de preços versionada em `common/pricing.yaml` (RF-07)."""

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel

PRICING_PATH = Path(__file__).with_name("pricing.yaml")


class ModelPrice(BaseModel):
    input: float | None  # US$ por 1M tokens
    output: float | None
    source: str


class Pricing(BaseModel):
    reference_date: str
    models: dict[str, ModelPrice]


class PricingMissingError(Exception):
    """O modelo não está na tabela ou está sem preço preenchido."""


@lru_cache
def load_pricing(path: Path = PRICING_PATH) -> Pricing:
    return Pricing.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def cost_usd(model: str, tokens_in: int | None, tokens_out: int | None) -> float:
    price = load_pricing().models.get(model)
    if price is None or price.input is None or price.output is None:
        raise PricingMissingError(f"sem preço para '{model}' em common/pricing.yaml")
    return ((tokens_in or 0) * price.input + (tokens_out or 0) * price.output) / 1_000_000
