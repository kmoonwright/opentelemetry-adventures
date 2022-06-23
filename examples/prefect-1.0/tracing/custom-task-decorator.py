import traceback
import os
from random import sample
from functools import partial, wraps
from prefect import task, Flow, Parameter, context
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# Opentelemetry initialization
resource = Resource(attributes={"service.name": "prefect-flows"})
otlp_exporter = OTLPSpanExporter(
    endpoint="https://api.honeycomb.io",
    headers=(
        ("x-honeycomb-team", os.getenv("HONEYCOMB_API_KEY", "")),
        ("x-honeycomb-dataset", os.getenv("HONEYCOMB_DATASET", "")),
    ),
)
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# PREFECT STUFF
@tracer.start_as_current_span("Task Init")
def otel_task(func=None, **task_init_kwargs):
    if func is None:
        return partial(otel_task, **task_init_kwargs)

    @tracer.start_as_current_span("Task Logic Init")
    @wraps(func)
    def safe_func(**kwargs):
        try:
            return func(**kwargs)
        except Exception as e:
            print(f"Full Traceback: {traceback.format_exc()}")
            raise RuntimeError(type(e)) from None  # from None is necessary to not log the stacktrace

    safe_func.__name__ = func.__name__
    return task(safe_func, **task_init_kwargs)


@otel_task(log_stdout=True)
def extract(length):
    nums = sample(range(100), length)
    logger = context.get("logger")
    logger.info(f"YOUR Numbers Are:...\n{nums}")
    return nums

@otel_task(log_stdout=True)
def transform(data: int):
    return data * 10

@otel_task(log_stdout=True)
def load(data):
    print(f"\nHere's your data: {data}")


with Flow('Evolving ETL') as flow:
    length = Parameter(name="length", default=3)
    e = extract(length)
    t = transform.map(e)
    l = load(t)

if __name__ == "__main__":
    flow.run()