# Peruvian Voucher ETL and API

## TLDR

To get minimally started, run the below commands from the root of the repository (please ensure you have docker, docker-compose, and kind installed on your machine -- requirements are enumerated in `Build Requirements` section):

Docker:

* `make docker_api`
  * If you want to check to make sure that API service is alive:
    * `curl localhost:8000/healthz`
* `curl -X POST localhost:8000/api/v1/voucher --header 'Content-Type: application/json' -d '{"customer_id": 123, "country_code": "Peru","last_order_ts": "2021-10-26 00:00:00", "first_order_ts": "2021-10-26 00:00:00", "total_orders": 14, "segment_name": "frequent_segment"}'`
  * response will be as follows:
    * `{"voucher": 2640}`
* cleanup can be run with `docker system prune -y`

Kubernetes:

* `make kind_cluster`
  * please note that the kind cluster instantiation is a bit finicky so the rollout status timeout is set pretty high as it takes a few minutes for the cluster to become stable
  * the kind cluster creates a `CronJob` for the ETL pipeline and then immediately triggers one job before instantiating the API
  * if the command initially fails, run `make cleanup_cluster` and retry running `make kind_cluster`
* `kubectl port-forward svc/api 8000:8000`
* `curl -X POST localhost:8000/api/v1/voucher --header 'Content-Type: application/json' -d '{"customer_id": 123, "country_code": "Peru","last_order_ts": "2021-10-26 00:00:00", "first_order_ts": "2021-10-26 00:00:00", "total_orders": 14, "segment_name": "frequent_segment"}'`
  * response will be as follows:
    * `{"voucher": 2640}`
* clean up can be run with `make cleanup_cluster`

For both the docker and kubernetes clusters, [swagger docs](https://swagger.io/docs/) for the API endpoints can be viewed and tested at `localhost:8000/docs`.

### Load Testing (docker and kubernetes)

Using a simple tool like [`hey`](https://github.com/rakyll/hey), we can get a feel for what type of load our API can handle. The image is being served with [`uvicorn`](https://www.uvicorn.org/) and 4 workers, but we also have the benefit in the kubernetes cluster to enable horizontal pod autoscaling. In this implementation, the scaling is pinned to CPUUtilization, but in production with a service mesh like [`Istio`](https://istio.io/), we can move to scale the pods based on reqeusts per second. Furthermore, we can use a load balancer for the cluster as well to help alleviate the load to one single pod. Examples of the docker and kubernetes (kind) load testing, and their output, can be found below:

* `docker`
  * `make docker_api`
    * wait for docker image to be attached
  * `hey -n 1000 -m POST -H 'Content-Type: application/json' -d '{"customer_id": 123, "country_code": "Peru","last_order_ts": "2021-10-26 00:00:00", "first_order_ts": "2021-10-26 00:00:00", "total_orders": 14, "segment_name": "frequent_segment"}' 'http://localhost:8000/api/v1/voucher'`
  * an example of the output is below:

```bash
Summary:
  Total: 0.5370 secs
  Slowest: 0.0724 secs
  Fastest: 0.0016 secs
  Average: 0.0233 secs
  Requests/sec: 1862.2940
```

* `kubernetes`
  * `make kind_cluster`
    * wait for cluster to stabilize and populate
  * `kubectl port-forward svc/api 8000:8000`
  * `hey -n 1000 -m POST -H 'Content-Type: application/json' -d '{"customer_id": 123, "country_code": "Peru","last_order_ts": "2021-10-26 00:00:00", "first_order_ts": "2021-10-26 00:00:00", "total_orders": 14, "segment_name": "frequent_segment"}' 'http://localhost:8000/api/v1/voucher'`
  * an example of the output is below:

```bash
Summary:
  Total: 0.7714 secs
  Slowest: 0.1119 secs
  Fastest: 0.0028 secs
  Average: 0.0351 secs
  Requests/sec: 1296.3578
```

### Build Requirements

A summary of my machine as well as tools that are being used to run testing are listed below. It is _strongly_ recommended to run every command through `docker` so as to not have strange discrepancies between different machine runtimes.

* `Python` version: `3.7.10`
* `Mac OSX` version: `11.6`
* `docker` version: `20.10.8`
* `docker-compose` version: `1.29.2`
* `kind` version: `0.11.1`

### Build Instructions

All builds are run through a Makefile, and a summary of the commands can be found below.

* the default make command runs the test suite
* `docker_echo` - `echo`s out messages to ensure proper system configuration
* `lint` - uses [`black`](https://github.com/psf/black/) to run linting
* `test` - runs the test suite in a docker environment
  * these tests contain unit tests for both the ETL and the API
* `build_docker` - builds the docker images for the ETL pipeline and the API
* `docker_api` - builds and runs the docker image for the API
* `docker_etl` - builds and runs the docker image for the ETL pipeline
* `kind_cluster` - builds and deploys an example cluster setup using [`kind`](https://kind.sigs.k8s.io/)
  * more detail on this is enumerated below
* `cleanup_cluster` - cleans up everything created for the kind cluster

### Exploratory Analysis

A jupyter notebook of some exploratory analysis of the data can be found in [this notebook](notebooks/data_exploration.ipynb).

### Makefile Breadown, Motivations, and Summary of Files

* `make_lint`
  * Never really required, but in larger organizations with more code being pushed out rapidly, having an opinionated linter helps keep code style uniform. In this repo, it's been configured as a pre-commit hook, but this can also be run as step in CI/CD.
* `make test`
  * unit and integration tests are run through [`pytest`](https://docs.pytest.org/en/6.2.x/), python has a huge amount of different testing libraries, but I've used pytest the most.
  * these tests are run in a docker image to control for any machine differences
* `make kind_cluster`
  * this is more of a preview for how this would be deployed in production, above I enumrated a lot of infrastructure differences, and this can be done through CI/CD with [`terraform`](https://www.terraform.io/)
  * since kind clusters are quasi-real clusters, we need to create a local docker registry to be able to reference our created docker images
  * [`build/kind/create-kind-registry.sh`](build/kind/create-kind-registry.sh) creates a local docker registry and network that can then be called by kind
  * [`build/kind/config.yaml`](build/kind/config.yaml) sets up our kind cluster by patching the containerd registry to pull from our locally set up registry and creates a node for us to deploy our pods to
    * this config also has some volume mounting information needed for our data files, in a true production setting these data files wouldn't be mounted to the images they would be connected through a DB or something of the like, but for our purposes, this is sufficient
  * finally these images are loaded and deployed into the cluster
  * the API instance can be exposed easily as well:
    * `kubectl port-forward svc/api 8000:8000`
* `make cleanup_cluster`
  * deletes kind cluster, kills and deletes the docker registry, and finally removes images

The `python` code should have inline comments as well as docstrings for comprehensibility.

#### Maintainer

* [Alex Lee](mailto:westford14@gmail.com)
