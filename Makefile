.PHONY: install verify format test run

install:
	python -m pip install -e '.[dev]'

verify:
	ruff format --check .
	ruff check .
	mypy src tests
	pytest

format:
	ruff format .
	ruff check . --fix

test:
	pytest

run:
	uvicorn reelore.bootstrap:build_default_app --factory --reload
