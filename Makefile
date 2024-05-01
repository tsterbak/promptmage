.PHONY: install test

install:
	poetry install

test:
	poetry run pytest tests --cov=flowforgeai --cov-report=term-missing