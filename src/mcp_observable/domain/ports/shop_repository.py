from typing import Protocol

from mcp_observable.domain.models.customer_summary import CustomerSummary
from mcp_observable.domain.models.monthly_revenue import MonthlyRevenue
from mcp_observable.domain.models.order import Order
from mcp_observable.domain.models.product_sales import ProductSales


class ShopRepository(Protocol):
    def search_orders(
        self, status: str | None, min_total: float, country: str | None, limit: int
    ) -> list[Order]: ...

    def customer_summary(self, customer_id: int) -> CustomerSummary | None: ...

    def top_products(self, category: str | None, limit: int) -> list[ProductSales]: ...

    def revenue_by_month(self, year: int) -> list[MonthlyRevenue]: ...

    def run_query(self, sql: str, limit: int) -> list[dict]: ...