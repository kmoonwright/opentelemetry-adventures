import prefect
from prefect import Task, Flow

from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(
   
    SimpleSpanProcessor(ConsoleSpanExporter())
)
class OtelTask1(Task):
    def run(self, num, **kwargs):
        logger = prefect.context.get("logger")
        logger.info("HELLO from Task 2")
        logger.info(F"MY ARG: {num}")

        with tracer.start_as_current_span("parent"):
            return num

class OtelTask2(Task):
    @tracer.start_as_current_span("Task Init")
    def run(self, num, **kwargs):
        logger = prefect.context.get("logger")
        logger.info("HELLO from Task 2")
        logger.info(F"MY ARG: {num}")
        
        return num


my_first_task = OtelTask1()
my_second_task = OtelTask2()

with Flow("Context Otel Flow 1") as flow1:
    my_first_task()

with Flow("Context Otel Flow 2") as flow2:
    my_second_task()

if __name__ == "__main__":
    flow1.run()
    flow2.run()