# Development

This document provides an overview of the development process for PromptMage. It includes information on the project structure, the development environment, and the development workflow.

## Install development environment

To install the development environment, follow these steps:

1. Clone the repository:

    ```bash
    git clone
    ```

2. Install the dependencies:

PromptMage uses [Poetry](https://python-poetry.org/) to manage dependencies. To install the dependencies, run the following command:

    ```bash
    poetry install
    ```

## Run Promptmage in development mode

To run PromptMage examples in development mode install the examples dependencies:

```bash
cd examples
poetry install
```

Then run the examples:

```bash
poetry run promptmage run summarize_article_by_facts.py
```

## Run tests

To run the tests, run the following command:

```bash
poetry run pytest .
```

## Style guide

PromptMage uses [Black](https://black.readthedocs.io/en/stable/) to format the code. To format the code, run the following command:

```bash
poetry run black .
```