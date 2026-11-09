import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_telemetry(service_name: str) -> None:
    endpoint = os.getenv(
        "OTEL_ENDPOINT",
        "http://localhost:4317",
    )

    resource = Resource.create({
        "service.name": service_name,
    })

    provider = TracerProvider(resource=resource)

    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=endpoint,
                insecure=True,
            )
        )
    )

    trace.set_tracer_provider(provider)