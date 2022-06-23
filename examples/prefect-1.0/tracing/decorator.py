import os
from prefect import Flow, Parameter, task, unmapped
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
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

# OTel State Handler
@tracer.start_as_current_span("Flow Configuration")
def flow_state_to_otel(obj, old_state, new_state):
    msg = "\nCalling my custom state handler on {0}:\n{1} to {2}\n"
    print(msg.format(obj, old_state, new_state))

    current_span = trace.get_current_span()
    current_span.set_attribute("flow.name", str(obj.name))
    current_span.set_attribute("flow.parameters", str(obj.parameters()))
    current_span.set_attribute("flow.executor", str(obj.executor))
    current_span.set_attribute("flow.run_config", str(obj.run_config))
    current_span.set_attribute("flow.diagnostics", obj.diagnostics())
    return new_state


# PREFECT TASKS
@task
@tracer.start_as_current_span("task_1")
def get_numbers(n):
    current_span = trace.get_current_span()
    current_span.set_attribute("task_1.arg", n)
    return range(1, n + 1)

@task
@tracer.start_as_current_span("task_2")
def increment(x):
    # Add span attibute
    current_span = trace.get_current_span()
    current_span.set_attribute("task_2.arg", x)
    return x + 1

@task
@tracer.start_as_current_span("task_3")
def add(x, y):
    return x + y

@task
@tracer.start_as_current_span("task_4")
def compute_sum(nums):
    total = sum(nums)
    print(f"total = {total}")
    return total

# FLOW CONTEXT
with Flow("Example: Decorator", state_handlers=[flow_state_to_otel]) as flow:
    n = Parameter("n", default=3)
    nums = get_numbers(n)  # [1, 2, 3]
    nums_2 = increment.map(nums)  # [2, 3, 4]
    nums_3 = add.map(nums_2, unmapped(2))  # [4, 5, 6]
    total = compute_sum(nums_3)  # 15


if __name__ == "__main__":
    flow.run()

 

 