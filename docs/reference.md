# API Reference

This page contains the API reference with the most important classes and methods of promptmage.

## PromptMage `class`

The `PromptMage` class is the main class of promptmage. It is used store all the information about the flow and to run the flow.

### Attributes

- **name** (`str`):  
  The name of the `PromptMage` instance.

- **available_models** (`List[str]`):  
  A list of available models to use for the flow.

!!! info

    The available models are just strings that are passed to the step function to specify the model to use for the completion. You have to handle the model selection in the step function.

### Methods

#### `PromptMage.step()` `decorator`

Decorator to define a step in the flow.

!!! tip

    A step is just a python function with the `@mage.step()` decorator which returns a `MageResult`.

##### Arguments

- **name** (`str`):  
  The name of the step.

- **prompt_name** (`str`):  
  The name of the prompt to use for this step.

- **initial** (`bool`):  
  Whether this is the initial step of the flow.

- **one_to_many** (`bool`):  
  Whether this step should be run for each item in the input list.

- **many_to_one** (`bool`):  
  Whether this step should be run for each item in the input list and the results should be combined.

---

## MageResult `class`

The `MageResult` class is used to return the result of a step.

### Attributes

- **next_step** (`str | None`):  
  The name of the next step to run.

- **error** (`str | None`):  
  An error message if the step failed.

- **\*\*kwargs** (`Any`):  
  All additional keyword arguments are stored as the result by name and can be used by the next step.

---

## Prompt `class`

The `Prompt` class is used to store the prompt information.

!!! warning
    
    This class should not be created by the user. It is automatically created by the `PromptMage` instance and only used to pass the prompt to the step functions and retrieve the prompts from the database.

### Attributes

- **system** (`str`):  
  The system prompt.

- **user** (`str`):  
  The user prompt.
