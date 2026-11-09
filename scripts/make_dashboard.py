
import json
from pathlib import Path

DASHBOARD_PATH = Path("infra/grafana/dashboards/mcp.json")

DATASOURCE = {
    "type": "prometheus",
    "uid": "prometheus",
}

CALLS = "mcp_tool_calls_total"
ERRORS = "mcp_tool_errors_total"
DURATION = "mcp_tool_duration_milliseconds_bucket"


def panel(
    panel_id: int,
    title: str,
    expression: str,
    *,
    kind: str = "timeseries",
    x: int = 0,
    y: int = 0,
    width: int = 12,
    height: int = 8,
    unit: str = "short",
    legend: str = "{{tool}}",
) -> dict:
    return {
        "id": panel_id,
        "title": title,
        "type": kind,
        "datasource": DATASOURCE,
        "gridPos": {
            "x": x,
            "y": y,
            "w": width,
            "h": height,
        },
        "targets": [
            {
                "expr": expression,
                "legendFormat": legend,
                "refId": "A",
            }
        ],
        "fieldConfig": {
            "defaults": {"unit": unit},
            "overrides": [],
        },
    }


panels = [
    panel(
        1,
        "Llamadas por minuto",
        f"sum(rate({CALLS}[5m])) * 60",
        kind="stat",
        x=0,
        y=0,
        width=8,
        height=4,
        legend="total",
    ),
    panel(
        2,
        "Porcentaje de errores",
        (
            f"sum(rate({ERRORS}[5m])) / "
            f"clamp_min(sum(rate({CALLS}[5m])), 1e-9)"
        ),
        kind="stat",
        x=8,
        y=0,
        width=8,
        height=4,
        unit="percentunit",
        legend="errores",
    ),
    panel(
        3,
        "Latencia p95 global",
        (
            "histogram_quantile(0.95, "
            f"sum by (le) (rate({DURATION}[5m])))"
        ),
        kind="stat",
        x=16,
        y=0,
        width=8,
        height=4,
        unit="ms",
        legend="p95",
    ),
    panel(
        4,
        "Llamadas por segundo y herramienta",
        f"sum by (tool) (rate({CALLS}[5m]))",
        x=0,
        y=4,
    ),
    panel(
        5,
        "Latencia p95 por herramienta",
        (
            "histogram_quantile(0.95, "
            f"sum by (le, tool) (rate({DURATION}[5m])))"
        ),
        x=12,
        y=4,
        unit="ms",
    ),
    panel(
        6,
        "Errores por herramienta y tipo",
        f"sum by (tool, error_type) (rate({ERRORS}[5m]))",
        x=0,
        y=12,
        width=24,
        legend="{{tool}} / {{error_type}}",
    ),
]

LLM_DURATION = "llm_call_duration_milliseconds_bucket"

panels.extend([
    panel(
        7,
        "Coste estimado última hora (USD)",
        "sum(increase(llm_cost_usd_total[1h]))",
        kind="stat",
        x=0,
        y=20,
        width=8,
        height=4,
        unit="currencyUSD",
        legend="coste",
    ),
    panel(
        8,
        "Tokens por segundo",
        "sum by (type) (rate(llm_tokens_total[5m]))",
        x=0,
        y=24,
        legend="{{type}}",
    ),
    panel(
        9,
        "Latencia p95 del LLM",
        (
            "histogram_quantile(0.95, "
            f"sum by (le, model) (rate({LLM_DURATION}[5m])))"
        ),
        x=12,
        y=24,
        unit="ms",
        legend="{{model}}",
    ),
])

dashboard = {
    "uid": "mcp-overview",
    "title": "MCP - Observabilidad",
    "schemaVersion": 39,
    "version": 1,
    "refresh": "5s",
    "time": {
        "from": "now-15m",
        "to": "now",
    },
    "panels": panels,
}

DASHBOARD_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

DASHBOARD_PATH.write_text(
    json.dumps(dashboard, indent=2),
    encoding="utf-8",
)

print(f"Dashboard generado: {DASHBOARD_PATH}")
