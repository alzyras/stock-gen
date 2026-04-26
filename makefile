.PHONY: env lint format test check requirements sync

env:
	python3 -m pip install uv
	uv sync --dev
	uv run pre-commit install

sync:
	uv sync --dev

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests
	uv run ruff check --fix src tests

test:
	uv run pytest

check:
	uv run python -m compileall -q src tests
	uv run ruff check src tests
	uv run pytest

requirements:
	uv export --no-dev --no-hashes --output-file requirements.txt
