PY=python -m py_compile
IMAGE_NAME = "interligo/discord-bot"
HEROKU_APP_NAME = "discord-bot-with-docker"
BOT_NAME = "FrameQuo"

build_image:
	docker build -t $(IMAGE_NAME) .

delete_image:
	docker rmi $(IMAGE_NAME)

push_image:
	docker push $(IMAGE_NAME)

push_heroku:
	heroku container:push web -a $(HEROKU_APP_NAME)

release_heroku:
	heroku container:release -a $(HEROKU_APP_NAME) web

logs:
	heroku logs --tail -a $(HEROKU_APP_NAME)

run:
	docker run -it --name $(BOT_NAME) $(IMAGE_NAME)

stop:
	docker stop $(BOT_NAME)

delete:
	docker rm $(BOT_NAME)
