.PHONY: help setup  run test lint format clean

RM = rm -rf
ifeq ($(OS),Windows_NT)
    RM = rmdir /s /q
endif

help: ## Muestra este mensaje de ayuda
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Instala uv y todas las dependencias del proyecto
	@echo "📦 Instalando dependencias con uv..."
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh | sh
	uv sync

run: ## Arranca el servidor FastMCP en modo producción (STDIO para Clientes IA)
	@echo "🔌 Servidor FastMCP listo para conexión..."
	uv run mcp-server

agent: ## Arranca el agente
	@echo "🔌 Running agent..."
	uv run agent

test: ## Ejecuta los tests unitarios
	@echo "🧪 Ejecutando pruebas con pytest..."
	uv run pytest tests/

lint: ## Revisa la calidad del código
	@echo "🔍 Analizando código con ruff..."
	uv run ruff check --fix src/ tests/

try: ## Ejecuta el cliente de prueba local
	@echo "🔌 Ejecutando cliente de prueba..."
	uv run python scripts/try_client.py

dashboard: ## Crea dashboard de grafana
	@echo "🔌 Creando dashboards en grafana..."
	uv run python scripts/make_dashboard.py

traffic: ## Genera trafico
	@echo "🔌 Generando trafico..."
	uv run python scripts/load_test.py

seed: ## Alimenta la base de datos
	@echo "🔌 Ejecutando seed..."
	uv run python scripts/seed.py

format: ## Formatea el código automáticamente
	@echo "✨ Formateando código con ruff..."
	uv run ruff format src/ tests/

clean: ## Limpia archivos temporales y entornos virtuales
	@echo "🧹 Limpiando temporales..."
	$(RM) .venv .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

infra-up: ## Levanta infrastructura necesaria
	@echo "🧹 Levantando infrastructura..."
	docker compose -f infra/docker-compose.yml up -d

infra-down: ## Detiene infrastructura
	@echo "🧹 Deteniendo infrastructura..."
	docker compose -f infra/docker-compose.yml down