import os
from dataclasses import asdict
from typing import Literal

from fastmcp import FastMCP

from mcp_observable.adapters.sqlite_shop_repository import SqliteShopRepository
from mcp_observable.observability.decorators import observed_tool

repo = SqliteShopRepository(os.getenv("DB_PATH", "data/shop.db"))
mcp = FastMCP(
    "shopdata-mcp",
)

Status = Literal["paid", "shipped", "delivered", "cancelled", "refunded"]
Category = Literal["portatiles", "perifericos", "redes", "almacenamiento", "audio"]


@mcp.tool()
@observed_tool()
def search_orders(
    min_total: float = 0.0,
    status: Status | None = None,
    country: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Busca pedidos por importe mínimo, estado y país del cliente (código ISO, por ejemplo ES). Máximo 50."""
    limit = max(1, min(limit, 50))
    return [asdict(o) for o in repo.search_orders(status, min_total, country, limit)]


@mcp.tool()
@observed_tool()
def customer_summary(customer_id: int) -> dict:
    """Resumen de un cliente: país, segmento, número de pedidos y valor total."""
    summary = repo.customer_summary(customer_id)
    if summary is None:
        raise ValueError(f"Cliente no encontrado: {customer_id}")
    return asdict(summary)


@mcp.tool()
@observed_tool()
def top_products(category: Category | None = None, limit: int = 5) -> list[dict]:
    """Productos que más facturan, opcionalmente de una categoría. Máximo 20."""
    limit = max(1, min(limit, 20))
    return [asdict(p) for p in repo.top_products(category, limit)]


@mcp.tool()
@observed_tool()
def revenue_by_month(year: int = 2026) -> list[dict]:
    """Facturación mensual de un año (solo pedidos pagados, enviados o entregados)."""
    return [asdict(m) for m in repo.revenue_by_month(year)]
