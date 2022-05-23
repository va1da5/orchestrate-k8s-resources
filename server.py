import json

import yaml
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


def make_test_job():
    NAMESPACE = "orchestrator"

    container_resources = client.V1ResourceRequirements(requests={"cpu": "0.5", "memory": "250M"})
    container = client.V1Container(
        name="bodywork",
        image="python:3.9.13-slim",
        image_pull_policy="Never",
        resources=container_resources,
        command=["sh"],
        args=["-c", "echo success; sleep 30"],
    )
    pod_spec = client.V1PodSpec(containers=[container], restart_policy="Never")
    pod_template_spec = client.V1PodTemplateSpec(spec=pod_spec)
    job_spec = client.V1JobSpec(template=pod_template_spec, completions=1, backoff_limit=4)
    job_metadata = client.V1ObjectMeta(
        namespace=NAMESPACE,
        name="job-test",
        labels={"app": "orchestrator"},
    )
    job = client.V1Job(metadata=job_metadata, spec=job_spec)

    api_instance = client.BatchV1Api()

    api_instance.create_namespaced_job(namespace=NAMESPACE, body=job)

    job_status = api_instance.read_namespaced_job_status(name="job-test", namespace=NAMESPACE)

    print(job_status)


@app.get("/")
def read_root():
    make_test_job()
    return {"Hello": "world"}


@app.get("/job/{job_name}", response_class=PlainTextResponse)
def read_ijob(job_name: str):
    api_instance = client.BatchV1Api()
    job = api_instance.read_namespaced_job(name=job_name, namespace="orchestrator")
    print(job)
    return ""


@app.get("/job/{job_name}/status", response_class=PlainTextResponse)
def read_job_status(job_name: str):
    api_instance = client.BatchV1Api()
    job = api_instance.read_namespaced_job_status(name=job_name, namespace="orchestrator")
    print(job)
    return ""


@app.get("/pod/{pod_name}/logs/", response_class=PlainTextResponse)
def read_pod_logs(pod_name: str):
    pod_logs = v1.read_namespaced_pod_log(name=pod_name, namespace="orchestrator")
    return pod_logs
