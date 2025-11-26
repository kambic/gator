# Beautified Git README and Docker Swarm Setup

## Reference Article

[Creating a Truly Distributed Microservice Architecture with Celery and Docker Swarm](https://liftoffllc.medium.com/creating-a-truly-distributed-microservice-architecture-with-celery-and-docker-swarm-e178198e6838)

## Create 10,000 Tasks Using API

```bash
curl http://0.0.0.0:5000/create_tasks/10000
```

## Docker Swarm Context Setup

```bash
# Create Docker context
docker context create vidra-03 --docker "host=ssh://bpl-vidra-03"

# List available contexts
docker context ls
# Output:
# NAME        DESCRIPTION                               DOCKER ENDPOINT                  ERROR
# default     Current DOCKER_HOST based configuration  unix:///var/run/docker.sock
# vidra-02 *  ssh://bpl-vidra-02
# vidra-03    ssh://bpl-vidra-03
```

## Swarm Stack Information

```bash
# List current stacks
docker stack ls
# Output:
# NAME        SERVICES
# calculator  7
# swarmpit    4

# List services for the calculator stack
docker stack services calculator
# Output:
# ID            NAME                        MODE        REPLICAS  IMAGE                  PORTS
# i6tne9afv7l0  calculator_addition         replicated  2/2       calc-addition:latest
# rwvcpgqez8ym  calculator_division         replicated  2/2       calc-division:latest
# oegcyddwjcam  calculator_flower          replicated  1/1       mher/flower:0.9.5       *:5555->5555/tcp
# r597vjavu1vt  calculator_multiplication   replicated  2/2       calc-multiplication:latest
# sfzaytxcoc63  calculator_producer         replicated  1/1       calc-producer:latest   *:5000->5000/tcp
# rmnkruaobrhx  calculator_rabbit           replicated  1/1       rabbitmq:management    *:15672->15672/tcp
# 89e78x7c2n2f  calculator_subtraction      replicated  2/2       calc-subtraction:latest
```

## Temporary Port Forwarding

```bash
ssh -fN -L 8080:localhost:8080 bpl-vidra-02.ts.telekom.si
ssh -fN -L 8888:localhost:888 bpl-vidra-02.ts.telekom.si
```

## Docker Stack Deploy and Registry Notes

```bash
docker stack deploy --compose-file=docker-compose.yml calculator

# Output:
# Ignoring unsupported options: build, links
# Since --detach=false was not specified, tasks will be created in the background.
# In a future release, --detach=false will become the default.
# Updating service calculator_multiplication (id: ...)
# image calc-multiplication:latest could not be accessed on a registry to record its digest.
# Each node will access calc-multiplication:latest independently, possibly leading to different nodes running different versions of the image.
# ...
```

# TODO registry push

❯ docker stack deploy --compose-file=docker-compose.yml calculator
Ignoring unsupported options: build, links

Since --detach=false was not specified, tasks will be created in the background.
In a future release, --detach=false will become the default.
Updating service calculator_multiplication (id: r597vjavu1vtm8s7gr7tf72or)
image calc-multiplication:latest could not be accessed on a registry to record
its digest. Each node will access calc-multiplication:latest independently,
possibly leading to different nodes running different
versions of the image.

Updating service calculator_division (id: rwvcpgqez8ymuj89orqbn4e8i)
image calc-division:latest could not be accessed on a registry to record
its digest. Each node will access calc-division:latest independently,
possibly leading to different nodes running different
versions of the image.

Updating service calculator_producer (id: sfzaytxcoc63oumne0mo74naq)
image calc-producer:latest could not be accessed on a registry to record
its digest. Each node will access calc-producer:latest independently,
possibly leading to different nodes running different
versions of the image.

Updating service calculator_rabbit (id: rmnkruaobrhx5x0s1rpv54dja)
Updating service calculator_flower (id: oegcyddwjcamdpzy1ky1kzwfl)
Updating service calculator_addition (id: i6tne9afv7l0vwqguzpik2f40)
image calc-addition:latest could not be accessed on a registry to record
its digest. Each node will access calc-addition:latest independently,
possibly leading to different nodes running different
versions of the image.

Updating service calculator_subtraction (id: 89e78x7c2n2fjm7onl0uvfqa0)
image calc-subtraction:latest could not be accessed on a registry to record
its digest. Each node will access calc-subtraction:latest independently,
possibly leading to different nodes running different
versions of the image.

vidra-kit/swarm on  master [?] via 🐳 vidra-02 took 10s
