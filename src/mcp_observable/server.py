from mcp_observable.adapters.mcp_tools import mcp
from mcp_observable.observability.decorators import observed_tool
from mcp_observable.observability.logs import setup_logging
from mcp_observable.observability.telemetry import setup_telemetry

setup_logging()
setup_telemetry("mcp_observable")

def main():
    """Punto de entrada para el script de consola"""
    mcp.run(transport="streamable-http", port=8000)


if __name__ == "__main__":
    main()
