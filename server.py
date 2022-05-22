from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from kubernetes import client, config

app = FastAPI()

try:
    config.load_incluster_config()
except config.ConfigException:
    try:
        config.load_kube_config()
    except config.ConfigException:
        raise Exception("Could not configure kubernetes python client")

v1 = client.CoreV1Api()


def make_pod():
    POD_NAME = "sleep-pod"
    NAMESPACE = "orchestrator"

    container = client.V1Container(
        name=POD_NAME, image="python:3.9.13-slim", command=["sh"], args=["-c", "echo success; sleep 30"]
    )

    pod_spec = client.V1PodSpec(containers=[container])
    pod_metadata = client.V1ObjectMeta(name=POD_NAME, namespace=NAMESPACE)

    pod_body = client.V1Pod(api_version="v1", kind="Pod", metadata=pod_metadata, spec=pod_spec)

    v1.create_namespaced_pod(namespace=NAMESPACE, body=pod_body)

    pod_logs = v1.read_namespaced_pod_log(name=POD_NAME, namespace=NAMESPACE)

    print(pod_logs)


def make_job():
    POD_NAME = "sleep-pod"
    NAMESPACE = "orchestrator"

    container = client.V1Container(
        name=POD_NAME, image="python:3.9.13-slim", command=["sh"], args=["-c", "echo success; sleep 30"]
    )

    # pod_spec = client.V1PodSpec(containers=[container])
    # pod_metadata = client.V1ObjectMeta(name=POD_NAME, namespace="orchestrator")

    # pod_body = client.V1Pod(api_version="v1", kind="Pod", metadata=pod_metadata, spec=pod_spec)

    # container = client.V1Container(image=image, command=commands, name=name, env=envs)

    pod_temp = client.V1PodTemplateSpec(
        spec=client.V1PodSpec(restart_policy="OnFailure", containers=[container]),
        metadata=client.V1ObjectMeta(name=POD_NAME, labels={"app": POD_NAME}),
    )

    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        spec=client.V1JobSpec(template=pod_temp),
        metadata=client.V1ObjectMeta(name=POD_NAME),
    )

    api_instance = client.BatchV1Api()

    # v1.create_namespaced_pod(namespace="orchestrator", body=pod_body)
    api_instance.create_namespaced_job(namespace=NAMESPACE, body=job)

    pod_logs = api_instance.read_namespaced_job(name=POD_NAME, namespace=NAMESPACE)

    print(pod_logs)


@app.get("/")
def read_root():
    print(make_job())

    return {"Hello": "world"}


@app.get("/logs/{pod_name}", response_class=PlainTextResponse)
def read_item(pod_name: str):
    pod_logs = v1.read_namespaced_pod_log(name=pod_name, namespace="orchestrator")
    return pod_logs
