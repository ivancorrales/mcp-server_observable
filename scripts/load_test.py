
import argparse
import asyncio
import random
import time

from collections import Counter

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


MCP_URL = "http://localhost:8000/mcp"

CATEGORIES = [
    "portatiles",
    "perifericos",
    "redes",
    "almacenamiento",
    "audio",
]

STATUSES = [
    "paid",
    "shipped",
    "delivered",
    "cancelled",
    "refunded",
]

COUNTRIES = ["ES", "PT", "FR", "DE", "IT", "MX"]


def generate_calls():
    """Genera llamadas variadas a las herramientas MCP."""

    calls = [
        (
            "top_products",
            {
                "limit": random.randint(1, 20),
                "category": random.choice(CATEGORIES + [None]),
            },
        ),
        (
            "search_orders",
            {
                "min_total": random.randint(0, 3000),
                "status": random.choice(STATUSES + [None]),
                "country": random.choice(COUNTRIES + [None]),
                "limit": random.randint(1, 50),
            },
        ),
        (
            "customer_summary",
            {
                "customer_id": random.randint(1, 200),
            },
        ),
        (
            "revenue_by_month",
            {
                "year": random.choice([2025, 2026]),
            },
        ),
    ]

    # Provocamos errores ocasionales para observarlos
    if random.random() < 0.15:
        calls.append(
            (
                "customer_summary",
                {"customer_id": 99999},
            )
        )

    random.shuffle(calls)

    return calls


async def run(delay: float):
    counters = Counter()
    start = time.perf_counter()

    async with streamable_http_client(MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("Conectado al servidor MCP")
            print("Generando tráfico... Ctrl+C para detener\n")

            while True:
                for tool, arguments in generate_calls():
                    t0 = time.perf_counter()

                    try:
                        result = await session.call_tool(
                            tool,
                            arguments,
                        )

                        elapsed = (
                            time.perf_counter() - t0
                        ) * 1000

                        counters["total"] += 1

                        if result.isError:
                            counters["errors"] += 1
                            status = "ERROR"
                        else:
                            counters["ok"] += 1
                            status = "OK"

                        print(
                            f"[{status}] "
                            f"{tool:<20} "
                            f"{elapsed:>8.2f} ms "
                            f"{arguments}"
                        )

                    except Exception as exc:
                        counters["total"] += 1
                        counters["errors"] += 1

                        print(
                            f"[EXCEPTION] {tool}: "
                            f"{type(exc).__name__}: {exc}"
                        )

                    if counters["total"] % 20 == 0:
                        seconds = time.perf_counter() - start

                        print(
                            "\n--- Estadísticas ---\n"
                            f"Llamadas: {counters['total']}\n"
                            f"Correctas: {counters['ok']}\n"
                            f"Errores: {counters['errors']}\n"
                            f"RPS: {counters['total'] / seconds:.2f}\n"
                            "--------------------\n"
                        )

                    await asyncio.sleep(delay)


def main():
    parser = argparse.ArgumentParser(
        description="Generador de tráfico continuo MCP"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Segundos entre llamadas (por defecto 0.2)",
    )

    args = parser.parse_args()

    if args.delay < 0:
        parser.error("--delay no puede ser negativo")

    try:
        asyncio.run(run(args.delay))
    except KeyboardInterrupt:
        print("\nGenerador detenido por el usuario.")


if __name__ == "__main__":
    main()
