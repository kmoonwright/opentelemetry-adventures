import os
from prefect import Flow, Parameter, task, unmapped, context
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

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

prop = TraceContextTextMapPropagator()
carrier = {}

# OTel State Handlers
@tracer.start_as_current_span("Flow Configuration")
def flow_state_to_otel(obj, old_state, new_state):
    msg = "\nCalling my custom state handler on {0}:\n{1} to {2}\n"
    # print(msg.format(obj, old_state, new_state))
    prop.inject(carrier=carrier)
    current_span = trace.get_current_span()
    current_span.set_attribute("flow.name", str(obj.name))
    current_span.set_attribute("flow.parameters", str(obj.parameters()))
    current_span.set_attribute("flow.executor", str(obj.executor))
    current_span.set_attribute("flow.run_config", str(obj.run_config))
    current_span.set_attribute("flow.diagnostics", obj.diagnostics())
    current_span.add_event(f"task.state == {old_state}")
    
    os.environ["parent_trace_id"] = str(prop.extract(carrier=carrier))

    return new_state

@tracer.start_as_current_span("Task State Diagnostics", context=os.getenv("parent_trace_id"))
def task_state_to_otel(obj, old_state, new_state):
    msg = "\nCalling my custom state handler on {0}:\n{1} to {2}\n"
    # print(msg.format(obj, old_state, new_state))
    
    current_span = trace.get_current_span()
    current_span.set_attribute("task.name", str(obj.name))
    current_span.set_attribute("task.task_run_name", str(obj.task_run_name))
    current_span.set_attribute("task.state", old_state)
    current_span.set_attribute("task.inputs", str(obj.inputs()))
    current_span.set_attribute("task.result", str(obj.result))
    current_span.set_attribute("task.target", str(obj.target))
    current_span.set_attribute("task.trigger", obj.trigger)
    current_span.add_event(f"STATE_CHANGE:{old_state} to {new_state}")

    # if hasattr(obj, "name"):
    #     current_span.set_attribute("task.name", str(obj.name))
    # elif hasattr(obj, "task_run_name"):
    #     current_span.set_attribute("task.task_run_name", str(obj.task_run_name))
    # elif hasattr(obj, "state"):
    #     current_span.set_attribute("task.state", obj.state)
    # elif hasattr(obj, "inputs"):
    #     current_span.set_attribute("task.inputs", obj.inputs)
    # elif hasattr(obj, "result"):
    #     current_span.set_attribute("result", obj.result)
    # elif hasattr(obj, "target"):
    #     current_span.set_attribute("task.target", obj.target)
    # elif hasattr(obj, "trigger"):
    #     current_span.set_attribute("task.trigger", obj.trigger)
    # else:
    #     pass

    return new_state


# PREFECT TASKS
@task(state_handlers=[task_state_to_otel])
def get_numbers(n):
    current_span = trace.get_current_span()
    current_span.set_attribute("task_1.arg", n)
    return range(1, n + 1)

@task(state_handlers=[task_state_to_otel])
def increment(x):
    # Add span attibute
    current_span = trace.get_current_span()
    current_span.set_attribute("task_2.arg", x)
    return x + 1

@task(state_handlers=[task_state_to_otel])
def add(x, y):
    return x + y

@task(state_handlers=[task_state_to_otel])
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

 

 