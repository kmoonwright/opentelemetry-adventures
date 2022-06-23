from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)
from opentelemetry.trace.propagation.tracecontext import \
    TraceContextTextMapPropagator

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

tracer = trace.get_tracer(__name__)

prop = TraceContextTextMapPropagator()
carrier = {}

# Injecting the context into carrier and send it over

with tracer.start_as_current_span("first-span") as span:
    prop.inject(carrier=carrier)
    print("Carrier after injecting span context", carrier)


# Extracting the remote context from carrier and starting a new span under same trace.

ctx = prop.extract(carrier=carrier)
with tracer.start_as_current_span("next-span", context=ctx):
    pass
