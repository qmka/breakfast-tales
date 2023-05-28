dev:
	poetry run flask --app breakfast_tales:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) breakfast_tales:app

lint:
	poetry run flake8

install:
	poetry install

check:
	poetry check