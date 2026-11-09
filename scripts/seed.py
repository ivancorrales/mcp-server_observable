import sqlite3

from mcp_observable.seed_data import generate

SCHEMA = '''
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT, country TEXT, segment TEXT);
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, ordered_at TEXT, status TEXT, total REAL);
CREATE TABLE order_items (order_id INTEGER, product_id INTEGER, qty INTEGER, unit_price REAL);
CREATE INDEX idx_orders_date ON orders(ordered_at);
CREATE INDEX idx_orders_customer ON orders(customer_id);
'''

customers, products, orders, items = generate()
con = sqlite3.connect('data/shop.db')
con.executescript(SCHEMA)
con.executemany('INSERT INTO customers VALUES (?,?,?,?,?)', customers)
con.executemany('INSERT INTO products VALUES (?,?,?,?)', products)
con.executemany('INSERT INTO orders VALUES (?,?,?,?,?)', orders)
con.executemany('INSERT INTO order_items VALUES (?,?,?,?)', items)
con.commit()
con.close()
print('ok', len(orders), 'pedidos')