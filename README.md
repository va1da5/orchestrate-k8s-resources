# Orchestrate Kubernetes API

WIP


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

## References

- [Namespaces Walkthrough](https://kubernetes.io/docs/tasks/administer-cluster/namespaces-walkthrough/)
- [Minikube Accessing apps](https://minikube.sigs.k8s.io/docs/handbook/accessing/)
- [Kubernetes Python Client](https://github.com/kubernetes-client/python)
- [A Beginner’s Guide to Kubernetes Python Client](https://www.velotio.com/engineering-blog/kubernetes-python-client)
- [Get started with Kubernetes (using Python)](https://kubernetes.io/blog/2019/07/23/get-started-with-kubernetes-using-python/)
- [Accessing the Kubernetes API from a Pod](https://kubernetes.io/docs/tasks/run-application/access-api-from-pod/)
- [Python kubernetes.config.load_incluster_config() Examples](https://www.programcreek.com/python/example/106725/kubernetes.config.load_incluster_config)
- [bodywork-core/tests/unit_and_functional/test_k8s_batch_jobs.py](https://github.com/bodywork-ml/bodywork-core/blob/00dc53861dd133823515690ef4a38d168b3659b5/tests/unit_and_functional/test_k8s_batch_jobs.py)
- [Minimal example for running on-demand K8s job using FastAPI](https://github.com/mloning/minimal-example-on-demand-k8s-job/tree/main)

