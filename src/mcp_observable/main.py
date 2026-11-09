import os

from mcp_observable.adapters.mcp.tools import mcp


def _parse_keys() -> dict[str, str]:
    raw = os.getenv('MCP_API_KEYS', 'dev-key-123:cliente-dev')
    return dict(pair.split(':', 1) for pair in raw.split(','))

# app = ApiKeyMiddleware(mcp.streamable_http_app(), _parse_keys(), TokenBucket(2.0, 10))
mcp.run(_parse_keys())