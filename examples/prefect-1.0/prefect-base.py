from datetime import datetime, timedelta
from random import sample
import prefect
from prefect import task, Flow, Parameter, case

@task
def extract(length):
    logger = prefect.context.get("logger")
    logger.info(prefect.context.today)
    return sample(range(100), length)

@task
def transform(data: int):
    prefect.context.get("hello")
    return data * 10

@task
def load(data):
    print(f"\nHere's your data: {data}")

with Flow("Dynamic ETL") as flow:

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