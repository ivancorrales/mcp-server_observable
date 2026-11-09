from dataclasses import dataclass


@dataclass(frozen=True)
class MonthlyRevenue:
    month: str
    orders: int
    revenue: float