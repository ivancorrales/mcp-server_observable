import json
import logging
import sys
from datetime import datetime, timezone
from opentelemetry import trace

class JsonFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
        }
        context = trace.get_current_span().get_span_context()

        payload["trace_id"] = (
            format(context.trace_id, "032x")
            if context.is_valid else None
        )
        payload["span_id"] = (
            format(context.span_id, "016x")
            if context.is_valid else None
        )

        payload.update(getattr(record, "fields", {}))

        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger("mcp_observable")

    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False