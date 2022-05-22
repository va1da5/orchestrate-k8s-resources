.PHONY: build
build:
	docker build -t orchestrator .

.PHONY: deploy
deploy:
	kubectl apply -f kubernetes/orchestrator.yml

.PHONY: restart
restart:
	@POD=$$(sh -c "kubectl get pods -n orchestrator | grep orchestrator | head -n 1 | cut -d' ' -f1"); \
	kubectl delete pod/$$POD -n orchestrator;

.PHONY: logs
logs:
	@POD=$$(sh -c "kubectl get pods -n orchestrator | grep orchestrator | head -n 1 | cut -d' ' -f1"); \
	kubectl logs -f -n orchestrator $$POD

.PHONY: url
url:
	@minikube service orchestrator-svc --url -n orchestrator
