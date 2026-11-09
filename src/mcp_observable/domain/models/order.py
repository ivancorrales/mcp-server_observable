from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    id: int
    customer_id: int
    ordered_at: str
    status: str
    total: float
