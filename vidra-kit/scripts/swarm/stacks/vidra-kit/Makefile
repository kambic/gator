
deploy:
	DOCKER_CONTEXT=vidra-02 docker stack deploy --detach=false -c docker-compose.yml vidra-kit

build:
	docker build -t gitlab.telekom.si:4567/vidra/vidra-kit workflows

push-img:
	docker push gitlab.telekom.si:4567/vidra/vidra-kit