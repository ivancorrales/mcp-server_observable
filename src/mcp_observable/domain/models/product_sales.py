from dataclasses import dataclass


@dataclass(frozen=True)
class ProductSales:
    product_id: int
    name: str
    category: str
    units: int
    revenue: float