from mcp_observable.adapters.mcp_tools import mcp
from mcp_observable.observability.decorators import observed_tool
from mcp_observable.observability.logs import setup_logging

setup_logging()

def main():
    """Punto de entrada para el script de consola"""
    mcp.run(transport="streamable-http", port=8000)


if __name__ == "__main__":
    main()
