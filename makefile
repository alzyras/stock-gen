.PHONY: env lint format test check requirements

env:
	pip3 install poetry pre-commit
	poetry install
	pre-commit install

lint:
	poetry run ruff check src tests

format:
	poetry run ruff format src tests
	poetry run ruff check --fix src tests

test:
	poetry run pytest

check:
	python3 -m compileall -q src
	poetry run ruff check src tests
	poetry run pytest

requirements:
	poetry export --without-hashes --without development -f requirements.txt -o requirements.txt
