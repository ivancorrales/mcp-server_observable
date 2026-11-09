import random
from datetime import datetime, timedelta

COUNTRIES = ['ES', 'PT', 'FR', 'DE', 'IT', 'MX']
SEGMENTS = ['particular', 'empresa', 'educacion']
CATEGORIES = ['portatiles', 'perifericos', 'redes', 'almacenamiento', 'audio']
STATUSES = ['paid', 'shipped', 'delivered', 'cancelled', 'refunded']


def generate(now: datetime = datetime(2026, 11, 1)):
    rnd = random.Random(7)
    customers = [
        (i, f'Cliente {i}', f'cliente{i}@example.com', rnd.choice(COUNTRIES), rnd.choice(SEGMENTS))
        for i in range(1, 201)
    ]
    products = [
        (i, f'Producto {i}', rnd.choice(CATEGORIES), round(rnd.uniform(9, 1500), 2))
        for i in range(1, 41)
    ]
    orders, items = [], []
    for order_id in range(1, 3001):
        customer_id = rnd.choice(customers)[0]
        when = now - timedelta(days=rnd.randint(0, 364), hours=rnd.randint(0, 23))
        total = 0.0
        for product in rnd.sample(products, rnd.randint(1, 4)):
            qty = rnd.randint(1, 3)
            total += qty * product[3]
            items.append((order_id, product[0], qty, product[3]))
        status = rnd.choices(STATUSES, weights=[5, 20, 60, 10, 5])[0]
        orders.append((order_id, customer_id, when.isoformat(timespec='seconds'), status, round(total, 2)))
    return customers, products, orders, items