# Orchestrate Kubernetes API

This is a simple (proof-of-concept) API layer on top of the Kubernetes API.  It is designed to provide a simple way to execute adhoc commands in a stand-alone containers as jobs.

## Setup

```bash
# create orchestrator resources
kubectl apply -f kubernetes/orchestrator.yml

# get list of pods in the namespace
kubectl get pods -n orchestrator

kubectl get jobs -n orchestrator

POD=$(kubectl get pods -n orchestrator | grep orchestrator | awk '{print $1}' | head -n 1)

# get list of pods in the namespace
kubectl get svc -n orchestrator

minikube service orchestrator-svc --url -n orchestrator

# get pod logs
kubectl logs -f -n orchestrator $POD

kubectl describe job/job-test -n orchestrator

# delete pod
kubectl delete pod/$POD -n orchestrator

kubectl delete pod/sleep-pod -n orchestrator
kubectl delete jobs/sleep-pod -n orchestrator


kubectl exec -it $POD -n orchestrator -- /bin/bash
```

## Testing

```bash
# To point your shell to minikube's docker-daemon, run:
eval $(minikube -p minikube docker-env)

# build container image with the orchestrator API
make build
# or 
docker build -t orchestrator .

# deploy orchestrator service to minikube
kubectl apply -f kubernetes/orchestrator.yml

# get minikube IP
SERVICE_ENDPOINT=$(minikube service orchestrator-svc --url -n orchestrator)

# check if service up and running
curl -s "${SERVICE_ENDPOINT}/"
# output:
# {"status":"alive"}

# create a job with a specific bash command
curl -s -X POST -H "Content-Type: application/json" \
   -d '{"cmd":"python3 -c \"import this\""}' "${SERVICE_ENDPOINT}/jobs"
# output:
# {"api_version":"batch/v1","kind":"Job","metadata":{"annotations":null,"cluster_name":null,"creation_timestamp":"2022-05-28T15:46:58+00:00","deletion_grace_period_seconds":null,"deletion_timestamp":null,"finalizers":null,"generate_name":null,"generation":1,"labels":{"app":"orchestrator"},"managed_fields":[{"api_version":"batch/v1","fields_type":"FieldsV1","fields_v1":{"f:metadata":{"f:labels":{".":{},"f:app":{}}},"f:spec":{"f:activeDeadlineSeconds":{},"f:backoffLimit":{},"f:completionMode":{},"f:completions":{},"f:parallelism":{},"f:suspend":{},"f:template":{"f:spec":{"f:containers":{"k:{\"name\":\"2152340b-bc32-4915-9f5c-2f02d0db84ef-container\"}":{".":{},"f:args":{},"f:command":{},"f:image":{},"f:imagePullPolicy":{},"f:name":{},"f:resources":{".":{},"f:requests":{".":{},"f:cpu":{},"f:memory":{}}},"f:terminationMessagePath":{},"f:terminationMessagePolicy":{}}},"f:dnsPolicy":{},"f:restartPolicy":{},"f:schedulerName":{},"f:securityContext":{},"f:terminationGracePeriodSeconds":{}}},"f:ttlSecondsAfterFinished":{}}},"manager":"OpenAPI-Generator","operation":"Update","subresource":null,"time":"2022-05-28T15:46:58+00:00"}],"name":"2152340b-bc32-4915-9f5c-2f02d0db84ef"....

# exprot job name/ID
export JOB=2152340b-bc32-4915-9f5c-2f02d0db84ef

# get list jobs
curl -s "${SERVICE_ENDPOINT}/jobs"
# output:
# [{"job":"2152340b-bc32-4915-9f5c-2f02d0db84ef","active":null,"completed_indexes":null,"completion_time":"2022-05-28T15:47:00+00:00","conditions":[{"last_probe_time":"2022-05-28T15:47:00+00:00","last_transition_time":"2022-05-28T15:47:00+00:00","message":null,"reason":null,"status":"True","type":"Complete"}],"failed":null,"ready":null,"start_time":"2022-05-28T15:46:58+00:00","succeeded":1,"uncounted_terminated_pods":null}]

# get job details
curl -s "${SERVICE_ENDPOINT}/jobs/${JOB}"
# output:
# {"api_version":"batch/v1","kind":"Job","metadata":{"annotations":null,"cluster_name":null,"creation_timestamp":"2022-05-28T15:46:58+00:00","deletion_grace_period_seconds":null,"deletion_timestamp":null,"finalizers":null,"generate_name":null,"generation":1,"labels":{"app":"orchestrator"},"managed_fields":[{"api_version":"batch/v1","fields_type":"FieldsV1","fields_v1":{"f:metadata":{"f:labels":{".":{},"f:app":{}}},"f:spec":{"f:activeDeadlineSeconds":{},"f:backoffLimit":{},"f:completionMode":{},"f:completions":{},"f:parallelism":{},"f:suspend":{},"f:template":{"f:spec":{"f:containers":{"k:{\"name\":\"2152340b-bc32-4915-9f5c-2f02d0db84ef-container\"}":{".":{},"f:args":{},"f:command":{},"f:image":{},"f:imagePullPolicy":{},"f:name":{},"f:resources":{".":{},"f:requests":{".":{},"f:cpu":{},"f:memory":{}}},"f:terminationMessagePath":{},"f:terminationMessagePolicy":{}}},"f:dnsPolicy":{},"f:restartPolicy":{},"f:schedulerName":{},"f:securityContext":{},"f:terminationGracePeriodSeconds":{}}},"f:ttlSecondsAfterFinished":{}}},"manager":"OpenAPI-Generator","operation":"Update","subresource":null,"time":"2022-05-28T15:46:58+00:00"},{"api_version":"batch/v1","fields_type":"FieldsV1","fields_v1":{"f:status":{"f:completionTime":{},"f:conditions":{},"f:startTime":{},"f:succeeded":{}}},"manager":"kube-controller-manager","operation":"Update","subresource":"status","time":"2022-05-28T15:47:00+00:00"}],"name":"2152340b-bc32-4915-9f5c-2f02d0db84ef","namespace":"orchestrator","owner_references":null,"resource_version":"25203","self_link":null,"uid":"15b34fb3-955a-4688-a54d-ffc6ada25c25"}.....

# get only job status
curl -s "${SERVICE_ENDPOINT}/jobs/${JOB}/status"
# output:
# {"active":null,"completed_indexes":null,"completion_time":"2022-05-28T16:11:18+00:00","conditions":[{"last_probe_time":"2022-05-28T16:11:18+00:00","last_transition_time":"2022-05-28T16:11:18+00:00","message":null,"reason":null,"status":"True","type":"Complete"}],"failed":null,"ready":null,"start_time":"2022-05-28T16:11:16+00:00","succeeded":1,"uncounted_terminated_pods":null}

# get job logs
curl -s "${SERVICE_ENDPOINT}/jobs/${JOB}/logs"
# output:
# The Zen of Python, by Tim Peters

# Beautiful is better than ugly.
# Explicit is better than implicit.
# Simple is better than complex.
# Complex is better than complicated.
# Flat is better than nested.
# Sparse is better than dense.
# Readability counts.
# Special cases aren't special enough to break the rules.
# Although practicality beats purity.
# Errors should never pass silently.
# Unless explicitly silenced.
# In the face of ambiguity, refuse the temptation to guess.
# There should be one-- and preferably only one --obvious way to do it.
# Although that way may not be obvious at first unless you're Dutch.
# Now is better than never.
# Although never is often better than *right* now.
# If the implementation is hard to explain, it's a bad idea.
# If the implementation is easy to explain, it may be a good idea.
# Namespaces are one honking great idea -- let's do more of those!

```

## References

- [Namespaces Walkthrough](https://kubernetes.io/docs/tasks/administer-cluster/namespaces-walkthrough/)
- [Minikube Accessing apps](https://minikube.sigs.k8s.io/docs/handbook/accessing/)
- [Kubernetes Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [Kubernetes Python Client](https://github.com/kubernetes-client/python)
- [A Beginner’s Guide to Kubernetes Python Client](https://www.velotio.com/engineering-blog/kubernetes-python-client)
- [Get started with Kubernetes (using Python)](https://kubernetes.io/blog/2019/07/23/get-started-with-kubernetes-using-python/)
- [Accessing the Kubernetes API from a Pod](https://kubernetes.io/docs/tasks/run-application/access-api-from-pod/)
- [Python kubernetes.config.load_incluster_config() Examples](https://www.programcreek.com/python/example/106725/kubernetes.config.load_incluster_config)
- [bodywork-core/tests/unit_and_functional/test_k8s_batch_jobs.py](https://github.com/bodywork-ml/bodywork-core/blob/00dc53861dd133823515690ef4a38d168b3659b5/tests/unit_and_functional/test_k8s_batch_jobs.py)
- [Minimal example for running on-demand K8s job using FastAPI](https://github.com/mloning/minimal-example-on-demand-k8s-job/tree/main)

