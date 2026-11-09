from dataclasses import dataclass


@dataclass(frozen=True)
class CustomerSummary:
    id: int
    name: str
    country: str
    segment: str
    orders: int
    lifetime_value: float
