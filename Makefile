.DEFAULT_GOAL := test 

.PHONY := test 
default: test ;

docker_echo:
	@echo "please ensure that you have docker and docker-compose installed on your system --"
	@echo "tested with docker version 20.10.8 and docker-compose version 1.29.2"

lint:
	pip install -r requirements-dev.txt
	black api/ --exclude api/tests
	black etl/ --exclude etl/etl_tests

test:
	make docker_echo 
	docker-compose -f build/docker/docker-compose-test.yaml up --build

docker_api:
	make docker_echo 
	docker-compose -f build/docker/docker-compose-api.yaml up --build

docker_etl:
	make docker_echo 
	docker-compose -f build/docker/docker-compose-etl.yaml up --build

build_docker:
	make docker_echo
	docker-compose -f build/docker/docker-compose-api.yaml build --no-cache
	docker-compose -f build/docker/docker-compose-etl.yaml build --no-cache

kind_cluster: 
	@echo "please ensure that you have kind installed on your system -- "
	@echo "tested with kind version 0.11.1"
	@echo "please also ensure that there is no kind cluster named 'westford14' already installed"
	bash build/kind/create-kind-registry.sh
	kind create cluster --config build/kind/config.yaml

	@echo "please ensure that you have kubectl installed on your system --"
	@echo "tested with kubctl version 1.21.2"
	kubectl config set-context $$(kubectl config current-context)

	@echo "deploying local images to cluster"
	docker network connect "kind" "kind-registry"
	make build_docker 
	kind load docker-image localhost:5000/api:latest --name westford14
	kind load docker-image localhost:5000/etl-pipeline:latest --name westford14
	kubectl apply -f build/k8s/
	@sleep 60
	kubectl create job --from=cronjob/etl-pipeline etl-pipeline-now 
	kubectl wait --for=condition=complete --timeout=120s job/etl-pipeline-now 
	kubectl rollout status deployment api --timeout=15m 

cleanup_cluster:
	@echo "cleaning up cluster and docker images and network"
	kind delete -v 4 cluster --name westford14
	docker kill kind-registry
	docker network rm kind 
	docker system prune -f 
