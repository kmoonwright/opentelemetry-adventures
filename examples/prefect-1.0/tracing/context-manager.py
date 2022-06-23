import os
from prefect import Flow, Parameter, task, unmapped
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

@task
def get_numbers(n): 
    nums = range(1, n + 1)
    current_span = trace.get_current_span()
    current_span.set_attribute("task.arg",nums)
    return nums

@task
def increment(x):
    return x + 1

@task
def add(x, y):
    return x + y

@task(log_stdout=True)
def compute_sum(nums):
    total = sum(nums)
    print(f"total = {total}")
    return total

with tracer.start_as_current_span("flow"):
    with Flow("Example: Context Manager") as flow:
        n = Parameter("n", default=3)

        with tracer.start_as_current_span("Task Block 1"):
            nums = get_numbers(n)  # [1, 2, 3]
            current_span = trace.get_current_span()
            current_span.set_attribute("task.nums", nums)
            
            with tracer.start_as_current_span("Task Block 2") as child:
                nums_2 = increment.map(nums)  # [2, 3, 4]
                nums_3 = add.map(nums_2, unmapped(2))  # [4, 5, 6]
                total = compute_sum(nums_3)  # 15


if __name__ == "__main__":
    flow.run()

 

 