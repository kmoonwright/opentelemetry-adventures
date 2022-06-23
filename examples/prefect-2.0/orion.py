from prefect import task, flow
from prefect.futures import PrefectFuture
import requests

def send_slack_alert_on_failure(task_future: PrefectFuture):
    task_future.wait()  # block until completion
    if task_future.get_state().is_failed():
        name_ = task_future.task_run.name
        id_ = task_future.task_run.flow_run_id
        requests.post(
            "https://hooks.slack.com/services/XXX/XXX/XXX",
            json={"text": f"The task `{name_}` failed in a flow run `{id_}`"},
        )

@task
def fail_successfully(x):
    return 1 / x

@flow
def main_flow(nr: int):
    future_obj = fail_successfully(nr)
    send_slack_alert_on_failure(future_obj)

if __name__ == "__main__":
    main_flow(nr=0)