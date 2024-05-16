.PHONY: install test build publish docs-build docs-serve format

install:
	poetry install

format:
	poetry run black promptmage

test:
	poetry run pytest tests --cov=promptmage --cov-report=term-missing

docs-build:
	poetry run mkdocs build

docs-serve:
	poetry run mkdocs serve

build:
	poetry build

publish:
	poetry publish --build