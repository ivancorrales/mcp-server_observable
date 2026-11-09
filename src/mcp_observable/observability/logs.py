import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
        }

        payload.update(getattr(record, "fields", {}))

        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger("mcp_observable")

    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False