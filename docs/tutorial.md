# Tutorial

Welcome to the PromptMage tutorial! This tutorial will guide you through the basics of PromptMage, and show you how integrate it into your own LLM project.

## Use case

For this tutorial, we want to build a simple multi-step LLM application. It contains multiple dependent steps, where the output of one step is used as the input for the next step. The application will be used to summarize an input text with extracting facts to summarize from.

The application will have the following steps:

- Step 1: Extract facts from a given text
- Step 2: Summarize the text using the extracted facts

We assume all the steps are implemented as separate Python functions that take input and return output in one python file `summarizer.py`.

## Step 1: Install PromptMage

First, we need to install PromptMage. You can install PromptMage using pip:

```bash
pip install promptmage
```

It is recommended to install PromptMage in a virtual environment to avoid conflicts with other packages.

## Step 2: Add PromptMage to your project

First, you need to add PromptMage to your project. You do that by adding the following to your `summarizer.py` file:

```python
# Create a new PromptMage instance
mage = PromptMage(name="fact-summarizer")
```

Next, you need to define the prompts and dependencies between the steps. You can do that by adding the following code to the functions in the `summarizer.py` file:

```python
@mage.step(name="extract", prompt_name="extract_facts", initial=True)
def extract_facts(article: str, prompt: Prompt) -> str:
    # <your application code here>
    return MageResult(facts=facts, next_step="summarize")
```

As a first step, this needs to be the initial step, so we set the `initial` parameter to `True`. This will be the first step that is executed when the application is run. Every step needs to return a `MageResult` object, which contains the output of the step and the name of the next step to be executed. In this case, the next step is the `summarize` step. Note, that you can also return a list of `MageResult` objects if you want to execute multiple steps in parallel.

```python
@mage.step(name="summarize", prompt_name="summarize_facts")
def summarize_facts(facts: str, prompt: Prompt) -> str:
    # <your application code here>
    return MageResult(summary=summary)
```

If the next_step is not specified, the step will be considered a terminal step and the application will stop after executing this step.

Now you can access the prompts within the step functions using the `prompt` argument. The `prompt` argument is an instance of the `Prompt` class, which provides methods to interact with the prompt.
By default we have a system and a user prompt available by `prompt.system` and `prompt.user` respectively. The prompts are later created in the web UI.

You don't need to worry about saving the prompts and data, PromptMage will take care of that for you.

## Step 3: Run the application

Now you can run the application by 

```bash
promptmage run summarizer.py
```

This will start the PromptMage web UI, where you can interact with the prompts and run and see the output of the steps.
You can access the web UI at `http://localhost:8000/gui/`.


More examples can be found in the [examples](https://github.com/tsterbak/promptmage/tree/main/examples) folder.