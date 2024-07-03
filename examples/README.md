# PromptMage Examples

This repository contains examples for using PromptMage in your application or workflow.

## Examples

- Article Summarizer: A simple multi-step LLM application that extracts facts from a given text and summarizes the text using the extracted facts. [View Example](https://github.com/tsterbak/promptmage/blob/main/examples/summarize_article_by_facts.py)

- Answer questions about YouTube videos: A multi-step LLM application that extracts information from a YouTube video and answers questions about the video. [View Example](https://github.com/tsterbak/promptmage/blob/main/examples/youtube_understanding.py)


## Getting Started

### Installation

Install the dependencies from the pyproject.toml file.

```bash
poetry install
```

### Usage

To use PromptMage, run the following command:

```bash
poetry run promptmage run <path-to-flow>.py
```


## Docker Example

You can find an usage example with docker here: [Docker example](https://github.com/tsterbak/promptmage/tree/main/examples/docker)