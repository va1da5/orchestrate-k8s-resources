from typing import Any, List, Mapping

from kubernetes.client.rest import ApiException

from kubernetes import client, config


class NoPodsFound(Exception):
    """Exception raised when no pods are found for a job"""


class JobAPIError(Exception):
    """Exception raised when a job API call fails"""


class JobNotFound(Exception):
    """Exception raised when a job is not found"""


NAMESPACE = "orchestrator"


try:
    config.load_incluster_config()
except config.ConfigException:
    try:
        config.load_kube_config()
    except config.ConfigException:
        raise Exception("Could not configure kubernetes python client")


coreV1Api = client.CoreV1Api()
batchV1Api = client.BatchV1Api()


def make_job(*, job_name: str, cmd: str = "echo success; sleep 30", namespace: str = NAMESPACE) -> Mapping[str, Any]:

    container_resources = client.V1ResourceRequirements(requests={"cpu": "0.5", "memory": "250M"})
    container = client.V1Container(
        name=f"{job_name}-container",
        image="python:3.9.13-slim",
        image_pull_policy="Never",
        resources=container_resources,
        command=["sh"],
        args=["-c", cmd],
    )
    pod_spec = client.V1PodSpec(containers=[container], restart_policy="Never")

    pod_template_spec = client.V1PodTemplateSpec(spec=pod_spec)

    job_spec = client.V1JobSpec(
        template=pod_template_spec,
        completions=1,
        backoff_limit=4,
        ttl_seconds_after_finished=60,
        active_deadline_seconds=120,
    )
    job_metadata = client.V1ObjectMeta(
        namespace=namespace,
        name=job_name,
        labels={"app": namespace},
    )
    job = client.V1Job(metadata=job_metadata, spec=job_spec)

    return batchV1Api.create_namespaced_job(namespace=namespace, body=job).to_dict()


def get_jobs(*, namespace: str = NAMESPACE) -> List[Mapping[str, Any]]:
    jobs = batchV1Api.list_namespaced_job(namespace=namespace)
    return [{"job": job.metadata.name, **job.status.to_dict()} for job in jobs.items]


def get_job(*, name: str, namespace: str = NAMESPACE) -> Mapping[str, Any]:
    try:
        job = batchV1Api.read_namespaced_job(name=name, namespace=namespace)
        return job.to_dict()
    except ApiException as exc:
        if exc.status == 404:
            raise JobNotFound("Job not found")
        raise JobAPIError("Failed to get job") from exc


def get_job_logs(*, name: str, namespace: str = NAMESPACE) -> str:
    pods = coreV1Api.list_namespaced_pod(namespace=namespace, label_selector=f"job-name={name}")
    if len(pods.items) == 0:
        raise NoPodsFound("No pods found for a job")
    pod_name = pods.items[len(pods.items) - 1].metadata.name
    try:
        pod_logs = coreV1Api.read_namespaced_pod_log(name=pod_name, namespace=namespace)
    except ApiException:
        return ""

    return pod_logs
