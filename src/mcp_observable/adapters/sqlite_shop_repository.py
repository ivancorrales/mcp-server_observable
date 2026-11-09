import sqlite3
from contextlib import closing

from mcp_observable.domain.models.customer_summary import CustomerSummary
from mcp_observable.domain.models.monthly_revenue import MonthlyRevenue
from mcp_observable.domain.models.order import Order
from mcp_observable.domain.models.product_sales import ProductSales

VALID_STATUS = ("paid", "shipped", "delivered")  # estados que cuentan como ingreso


class SqliteShopRepository:
    def __init__(self, path: str):
        self._path = path

    def _conn(self) -> sqlite3.Connection:
        # mode=ro: aunque el código fallara, no se puede escribir
        con = sqlite3.connect(f"file:{self._path}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        return con

    def search_orders(self, status, min_total, country, limit):
        sql = """
            SELECT o.id, o.customer_id, o.ordered_at, o.status, o.total
            FROM orders o JOIN customers c ON c.id = o.customer_id
            WHERE o.total >= ?
        """
        params: list = [min_total]
        if status:
            sql += " AND o.status = ?"
            params.append(status)
        if country:
            sql += " AND c.country = ?"
            params.append(country)
        sql += " ORDER BY o.total DESC LIMIT ?"
        params.append(limit)
        with closing(self._conn()) as con:
            return [Order(**dict(r)) for r in con.execute(sql, params)]

    def customer_summary(self, customer_id):
        sql = """
            SELECT c.id, c.name, c.country, c.segment,
                   COUNT(o.id) AS orders, COALESCE(SUM(o.total), 0) AS lifetime_value
            FROM customers c
            LEFT JOIN orders o ON o.customer_id = c.id AND o.status IN (?,?,?)
            WHERE c.id = ? GROUP BY c.id
        """
        with closing(self._conn()) as con:
            row = con.execute(sql, (*VALID_STATUS, customer_id)).fetchone()
        return CustomerSummary(**dict(row)) if row else None

    def top_products(self, category, limit):
        sql = """
            SELECT p.id AS product_id, p.name, p.category, SUM(i.qty) AS units,
                   ROUND(SUM(i.qty * i.unit_price), 2) AS revenue
            FROM order_items i
            JOIN products p ON p.id = i.product_id
            JOIN orders o ON o.id = i.order_id AND o.status IN (?,?,?)
        """
        params: list = list(VALID_STATUS)
        if category:
            sql += " WHERE p.category = ?"
            params.append(category)
        sql += " GROUP BY p.id ORDER BY revenue DESC LIMIT ?"
        params.append(limit)
        with closing(self._conn()) as con:
            return [ProductSales(**dict(r)) for r in con.execute(sql, params)]

    def revenue_by_month(self, year):
        sql = """
            SELECT strftime('%Y-%m', ordered_at) AS month, COUNT(*) AS orders,
                   ROUND(SUM(total), 2) AS revenue
            FROM orders
            WHERE strftime('%Y', ordered_at) = ? AND status IN (?,?,?)
            GROUP BY month ORDER BY month
        """
        with closing(self._conn()) as con:
            return [MonthlyRevenue(**dict(r)) for r in con.execute(sql, (str(year), *VALID_STATUS))]
