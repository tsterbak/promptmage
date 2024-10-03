# API Reference

This page contains the API reference with the most important classes and methods of promptmage.


## PromptMage CLI

The `promptmage` CLI is the command line interface to run the promptmage server and interact with the promptmage backend.


### version
Show the installed promptmage version.

Usage:
```bash
promptmage version
```

### run
Run a flow with the given path. A flow is a python script that defines the flow of the promptmage application.

Usage:
```bash
promptmage run <path-to-flow>
```

Available options:
- **`--port`** (`int`):  
  The port to run the server on. Default is `8000`.
- **`--host`** (`str`):
  The host to run the server on. Default is `localhost`.

### serve
Start the promptmage backend server.

Usage:
```bash
promptmage serve
```

Available options:
- **`--port`** (`int`):  
  The port to run the server on. Default is `8021`.
- **`--host`** (`str`):  
  The host to run the server on. Default is `localhost`.
  
### export
Export the promptmage database to json.

Usage:
```bash
promptmage export --filename <filename>
```

Available options:
- **`--filename`** (`str`):  
  The filename to export the database to.
- **`--runs`** (`bool`):  
  Whether to export the runs as well. Default is `False`.
- **`--prompts`** (`bool`):  
  Whether to export the prompts as well. Default is `False`.

### backup
Backup the promptmage database to a json file.

Usage:
```bash
promptmage backup --json_path <json_path>
```

Available options:
- **`--json_path`** (`str`):  
  The path to the json file to backup the database to.

### restore
Restore the promptmage database from a json file.


!!! warning

    This will ask for confirmation before restoring and will overwrite the current database.

Usage:
```bash
promptmage restore --json_path <json_path>
```

Available options:
- **`--json_path`** (`str`):  
  The path to the json file to restore the database from.






## PromptMage `class`

The `PromptMage` class is the main class of promptmage. It is used store all the information about the flow and to run the flow.

### Attributes

- **name** (`str`):  
  The name of the `PromptMage` instance.

- **remote** (`str`):  
  The URL of the remote backend to use. If this is set, the `PromptMage` instance will use the remote backend instead of the local one.

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
