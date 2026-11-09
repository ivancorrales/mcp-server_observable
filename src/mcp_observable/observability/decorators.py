import functools
import inspect
import logging
import time

from contextlib import contextmanager


log = logging.getLogger("mcp_observable.tools")


@contextmanager
def _observe(tool: str):
    start = time.perf_counter()

    fields = {
        "tool": tool,
        "status": "ok",
    }

    try:
        yield

    except Exception as exc:
        fields["status"] = "error"
        fields["error_type"] = type(exc).__name__
        raise
    finally:
        fields["duration_ms"] = round(
            (time.perf_counter() - start) * 1000,
            2,
        )
        log.info("tool_call", extra={"fields": fields})


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