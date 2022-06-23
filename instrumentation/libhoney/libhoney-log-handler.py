import logging
import requests
import os
import libhoney


import prefect
from prefect import task, Flow
from prefect.utilities.logging import get_logger


class HoneycombHandler(logging.StreamHandler):
    def emit(self, record):
        logger = prefect.context.get("logger")
        logger.debug(f"Record: {record}\n")

        libhoney.init(
            writekey=os.getenv("HONEYCOMB_API_KEY"), 
            dataset=os.getenv("HONEYCOMB_DATASET"),
            debug=True)
        ev = libhoney.Event(
            data={
                "name": record.name,
                "message.python": record.msg,
                "args": record.args,
                "levelname": record.levelname,
                "module": record.module,
                "message.prefect": record.message,
                "asctime": record.asctime,
                "msecs": record.msecs,
            })

        if hasattr(record, "flow_name"):
            ev.add_field("flow_name", record.flow_name)
        elif hasattr(record, "flow_run_id"):
            ev.add_field("flow_run_id", record.flow_run_id)
        elif hasattr(record, "task_name"):
            ev.add_field("task_name", record.flow_run_itask_named)
        elif hasattr(record, "task_run_id"):
            ev.add_field("task_run_id", record.task_run_id)
        elif hasattr(record, "task_slug"):
            ev.add_field("task_slug", record.task_slug)
        else:
            pass
        ev.send()

class RequestsHandler(logging.StreamHandler):
    def emit(self, record):
        logger = prefect.context.get("logger")
        logger.debug(f"Record: {record}\n")
        requests.post(
            url="https://api.honeycomb.io",
            headers=(
                ("x-honeycomb-team", os.getenv("HONEYCOMB_API_KEY", "")),
                ("x-honeycomb-dataset", os.getenv("HONEYCOMB_DATASET", "Prefect Flows")),
            ),
            # json = record,
        )


@task(name="Task A")
def task_a():
    return 3


@task(name="Task B")
def task_b(x):
    logger = prefect.context.get("logger")
    logger.debug("Beginning to run Task B with input {}".format(x))
    y = 3 * x + 1
    logger.debug("Returning the value {}".format(y))
    return y


with Flow("custom-log-handler") as flow:
    result = task_b(task_a)


# Attach custom logger, can be Flow or Task (defaults to Runner)
custom_logger = get_logger()
custom_logger.addHandler(HoneycombHandler())


if __name__ == "__main__":
    flow.run()

def read_responses(resp_queue):
    '''read responses from the libhoney queue, print them out.'''
    while True:
        resp = resp_queue.get()
        # libhoney will enqueue a None value after we call libhoney.close()
        if resp is None:
            break
        status = "sending event with metadata {} took {}ms and got response code {} with message \"{}\" and error message \"{}\"".format(
            resp["metadata"], resp["duration"], resp["status_code"],
            resp["body"].rstrip(), resp["error"])
        print(status)

read_responses(libhoney.responses())