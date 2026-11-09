import sqlite3

import pytest

from mcp_observable.adapters.sqlite_shop_repository import SqliteShopRepository


@pytest.fixture
def repo(tmp_path):
    db = tmp_path / "shop.db"
    con = sqlite3.connect(db)
    con.executescript("""
        CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT, country TEXT, segment TEXT);
        CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
        CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, ordered_at TEXT, status TEXT, total REAL);
        CREATE TABLE order_items (order_id INTEGER, product_id INTEGER, qty INTEGER, unit_price REAL);
        INSERT INTO customers VALUES (1, 'Ana', 'ana@example.com', 'ES', 'particular');
        INSERT INTO products VALUES (1, 'Portatil X', 'portatiles', 1000.0);
        INSERT INTO orders VALUES (1, 1, '2026-03-01T10:00:00', 'paid', 1000.0);
        INSERT INTO orders VALUES (2, 1, '2026-03-05T10:00:00', 'cancelled', 500.0);
        INSERT INTO order_items VALUES (1, 1, 1, 1000.0);
        INSERT INTO order_items VALUES (2, 1, 1, 500.0);
    """)
    con.close()
    return SqliteShopRepository(str(db))


def test_search_orders_filters_by_status_and_total(repo):
    assert [o.id for o in repo.search_orders("paid", 100.0, None, 10)] == [1]


def test_customer_summary_ignores_cancelled(repo):
    summary = repo.customer_summary(1)
    assert summary.orders == 1
    assert summary.lifetime_value == 1000.0


def test_customer_summary_missing(repo):
    assert repo.customer_summary(999) is None


def test_revenue_by_month(repo):
    months = repo.revenue_by_month(2026)
    assert [(m.month, m.orders, m.revenue) for m in months] == [("2026-03", 1, 1000.0)]


def test_top_products_excludes_cancelled(repo):
    top = repo.top_products(None, 5)
    assert top[0].name == "Portatil X"
    assert top[0].units == 1


def test_connection_is_read_only(repo):
    with pytest.raises(sqlite3.OperationalError):
        repo._conn().execute("DELETE FROM orders")
