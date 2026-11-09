import functools
import inspect
import logging
import time
from contextlib import contextmanager
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry import metrics

tracer = trace.get_tracer("mcp_observable")
log = logging.getLogger("mcp_observable.tools")

meter = metrics.get_meter("mcp_observable")

calls = meter.create_counter(
    "mcp_tool_calls",
    description="Llamadas a herramientas MCP",
)

errors = meter.create_counter(
    "mcp_tool_errors",
    description="Errores en herramientas MCP",
)

latency = meter.create_histogram(
    "mcp_tool_duration",
    unit="ms",
    description="Duración de las herramientas",
)


@contextmanager
def _observe(tool: str):
    start = time.perf_counter()

    fields = {
        "tool": tool,
        "status": "ok",
    }

    with tracer.start_as_current_span(
        f"mcp.tool.{tool}"
    ) as span:

        span.set_attribute("mcp.tool.name", tool)

        try:
            yield

        except Exception as exc:
            fields["status"] = "error"
            fields["error_type"] = type(exc).__name__

            span.record_exception(exc)
            span.set_status(
                Status(StatusCode.ERROR)
            )
            errors.add(
                1,
                {
                    "tool": tool,
                    "error_type": type(exc).__name__,
                },
            )
            raise

        finally:
            duration_ms = (
                time.perf_counter() - start
            ) * 1000

            fields["duration_ms"] = round(duration_ms, 2)
            attributes = {
                "tool": tool,
                "status": fields["status"],
            }

            calls.add(1, attributes)
            latency.record(duration_ms, attributes)
            log.info(
                "tool_call",
                extra={"fields": fields},
            )


def observed_tool(name: str | None = None):

    def decorator(fn):
        tool = name or fn.__name__

        if inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                with _observe(tool):
                    return await fn(*args, **kwargs)

            return async_wrapper

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with _observe(tool):
                return fn(*args, **kwargs)

        return wrapper

    return decorator

