.PHONY: install verify format test

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
