import uvicorn

from mcp_observable.adapters.mcp_tools import mcp
from mcp_observable.observability.logs import setup_logging
from mcp_observable.observability.telemetry import setup_telemetry
from mcp_observable.observability.propagation import TraceContextMiddleware


def main():
    """Punto de entrada para el script de consola."""

    setup_logging()
    setup_telemetry("mcp_observable")

    # Crear la aplicación HTTP de FastMCP
    app = mcp.http_app(
        path="/mcp",
        stateless_http=True,
    )

    # Añadir propagación de contexto OpenTelemetry
    app.add_middleware(TraceContextMiddleware)

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )


if __name__ == "__main__":
    main()