import logging

import pytest

from mcp_observable.observability.decorators import observed_tool


def test_observed_tool_success(caplog):
    @observed_tool("double")
    def double(value: int) -> int:
        return value * 2

    with caplog.at_level(
        logging.INFO,
        logger="mcp_observable.tools",
    ):
        result = double(5)

    assert result == 10

    record = next(
        r for r in caplog.records
        if r.message == "tool_call"
    )

    assert record.fields["tool"] == "double"
    assert record.fields["status"] == "ok"
    assert record.fields["duration_ms"] >= 0


def test_observed_tool_error(caplog):
    @observed_tool("failed")
    def failed():
        raise ValueError("Ejemplo de error")

    with caplog.at_level(
        logging.INFO,
        logger="mcp_observable.tools",
    ):
        with pytest.raises(ValueError):
            failed()

    record = next(
        r for r in caplog.records
        if r.message == "tool_call"
    )

    assert record.fields["status"] == "error"
    assert record.fields["error_type"] == "ValueError"