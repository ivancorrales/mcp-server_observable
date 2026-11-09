.PHONY: help install dev run test lint format clean

RM = rm -rf
ifeq ($(OS),Windows_NT)
    RM = rmdir /s /q
endif

help: ## Muestra este mensaje de ayuda
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Instala uv y todas las dependencias del proyecto
	@echo "📦 Instalando dependencias con uv..."
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh | sh
	uv sync

dev: ## Arranca el servidor FastMCP en modo desarrollo (Con interfaz web Inspector)
	@echo "🚀 Iniciando servidor FastMCP en modo desarrollo..."
	uv run fastmcp dev src/mcp_observable/main.py

run: ## Arranca el servidor FastMCP en modo producción (STDIO para Clientes IA)
	@echo "🔌 Servidor FastMCP listo para conexión..."
	uv run python src/mcp_observable/main.py

test: ## Ejecuta los tests unitarios
	@echo "🧪 Ejecutando pruebas con pytest..."
	uv run pytest tests/

lint: ## Revisa la calidad del código
	@echo "🔍 Analizando código con ruff..."
	uv run ruff check --fix src/ tests/

format: ## Formatea el código automáticamente
	@echo "✨ Formateando código con ruff..."
	uv run ruff format src/ tests/

clean: ## Limpia archivos temporales y entornos virtuales
	@echo "🧹 Limpiando temporales..."
	$(RM) .venv .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
