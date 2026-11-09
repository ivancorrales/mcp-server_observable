
import argparse
import asyncio
import random
import time

from mcp_observable.client.agent import run
from mcp_observable.observability.telemetry import flush_telemetry


QUESTIONS = [
    "¿Cuáles son los cinco productos que más facturan?",
    "¿Cuánto hemos facturado por mes en 2026?",
    "Dame el resumen del cliente 42",
    "Busca pedidos pagados de más de 1000 euros",
    "¿Cuáles son los productos más vendidos de la categoría audio?",
    "Busca los diez pedidos más caros de clientes españoles",
    "Dame el resumen del cliente 150",
    "¿Qué ingresos tuvimos en 2025?",
]


async def load_test(delay: float):
    total = 0
    errors = 0
    tokens_in = 0
    tokens_out = 0
    cost = 0.0

    print("Generando tráfico continuo con Ollama + MCP")
    print("Pulsa Ctrl+C para detener\n")

    try:
        while True:
            question = random.choice(QUESTIONS)
            start = time.perf_counter()

            try:
                result = await run(question)

                total += 1
                tokens_in += result.tokens_in
                tokens_out += result.tokens_out
                cost += result.cost_usd

                if not result.tools_called:
                    print("AVISO: El agente no llamó a herramientas")

                print(
                    f"\n[{total}] {question}\n"
                    f"Tools: {result.tools_called}\n"
                    f"Tokens: {result.tokens_in} + {result.tokens_out}\n"
                    f"Coste estimado: ${result.cost_usd:.5f}\n"
                    f"Duración: {result.seconds:.2f}s"
                )

            except Exception as exc:
                errors += 1
                print(
                    f"[ERROR] {type(exc).__name__}: {exc}"
                )

            if total > 0 and total % 5 == 0:
                print(
                    "\n--- ESTADÍSTICAS ACUMULADAS ---\n"
                    f"Consultas correctas: {total}\n"
                    f"Errores: {errors}\n"
                    f"Tokens entrada: {tokens_in}\n"
                    f"Tokens salida: {tokens_out}\n"
                    f"Coste estimado: ${cost:.5f}\n"
                    "--------------------------------\n"
                )

            await asyncio.sleep(delay)

    finally:
        # Exportar la telemetría pendiente
        flush_telemetry()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Segundos de pausa entre consultas",
    )

    args = parser.parse_args()

    try:
        asyncio.run(load_test(args.delay))
    except KeyboardInterrupt:
        print("\nPrueba detenida.")


if __name__ == "__main__":
    main()
