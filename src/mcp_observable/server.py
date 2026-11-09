from mcp_observable.adapters.mcp_tools import mcp


def main():
    """Punto de entrada para el script de consola"""
    mcp.run(transport="streamable-http", port=8000)


if __name__ == "__main__":
    main()
