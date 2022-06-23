import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

log_stream = logging.StreamHandler(sys.stdout)
stream_formatter = logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s')
log_stream.setFormatter(stream_formatter)
logger.addHandler(log_stream)

from random import sample
from prefect import task, Flow, Parameter, case

@task
def extract(length):
    return sample(range(100), length)

@task
def transform(data: int):
    return data * 10

@task
def load(data):
    print(f"\nHere's your data: {data}")

from prefect.schedules import Schedule
from prefect.schedules.clocks import IntervalClock

with Flow(
    "Evolving ETL", 
    # schedule=schedule
    ) as flow:

    length = Parameter(name="length", default=3)
    with case(length, 6):
        e = extract(length)
        t = transform.map(e)
        l = load(t)

    with case(length, 50):
        e = extract(length)
        t = transform.map(e)
        t2 = transform.map(t)
        l = load(t2)

if __name__ == "__main__":
    flow.run()