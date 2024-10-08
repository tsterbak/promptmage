<br />
<div align="center">
  <a href="https://github.com/tsterbak/promptmage">
    <img src="images/promptmage-logo.png" alt="PromptMage-Logo" width="120" height="120">
  </a>

  <h1 align="center">PromptMage</h1>

  <p align="center">
    simplifies the process of creating and managing LLM workflows as a self-hosted solution.
  </p>
  
  [![License](https://img.shields.io/github/license/tsterbak/promptmage?color=green)](https://github.com/tsterbak/promptmage/blob/main/LICENSE)
  [![Monthly downloads](https://img.shields.io/pypi/dm/promptmage
)](https://pypi.org/project/promptmage/)
  [![PyPI version](https://img.shields.io/pypi/v/promptmage)](https://pypi.org/project/promptmage/)
  [![GitHub issues](https://img.shields.io/github/issues/tsterbak/promptmage)](https://github.com/tsterbak/promptmage/issues)
  [![GitHub stars](https://img.shields.io/github/stars/tsterbak/promptmage)](https://github.com/tsterbak/promptmage/stargazers)
</div>

> [!WARNING]
> This application is currently in alpha state and under active development. Please be aware that the API and features may change at any time.


## About the Project

"PromptMage" is designed to offer an intuitive interface that simplifies the process of creating and managing LLM workflows as a self-hosted solution. It facilitates prompt testing and comparison, and it incorporates version control features to help users track the development of their prompts. Suitable for both small teams and large enterprises, "PromptMage" seeks to improve productivity and foster the practical use of LLM technology.

The approach with "PromptMage" is to provide a pragmatic solution that bridges the current gap in LLM workflow management. We aim to empower developers, researchers, and organizations by making LLM technology more accessible and manageable, thereby supporting the next wave of AI innovations.

![PromptMage](https://github.com/tsterbak/promptmage/blob/main/docs/images/screenshots/plaground-dark.png)

Take the [walkthrough](https://promptmage.io/walkthrough/) to see what you can do with PromptMage.

## Philosophy
- Integrate the prompt playground into your workflow for fast iteration
- Prompts as first-class citizens with version control and collaboration features
- Manual and automatic testing and validation of prompts
- Easy sharing of results with domain experts and stakeholders
- build-in, automatically created API with fastAPI for easy integration and deployment
- Type-hint everything for automatic inference and validation magic

## Projects using PromptMage

- [product-review-research](https://github.com/tsterbak/product-review-research): An AI webapp build with PromptMage to provide in-depth analysis for products by researching trustworthy online reviews. 

## Getting Started

### Installation

To install promptmage, run the following command:

```bash
pip install promptmage 
```

## Usage

To use promptmage, run the following command:

```bash
promptmage run <path-to-flow>
```

This will start the local promptmage server and run the flow at the given path. You can now access the promptmage interface at `http://localhost:8000/gui/`.

To run the remote backend server, run the following command:

```bash
promptmage serve --port 8021
```

To make it work with your promptmage script, you should add the following lines to your script:

```python
from promptmage import PromptMage

mage = PromptMage(remote="http://localhost:8021")  # or the URL of your remote server
```

Have a look at the examples in the [examples](https://github.com/tsterbak/promptmage/tree/main/examples) folder to see how to use promptmage in your application or workflow.


## Use with Docker

You can find an usage example with docker here: [Docker example](https://github.com/tsterbak/promptmage/tree/main/examples/docker).


## Development

To develop PromptMage, check out the [DEVELOPMENT.md](DEVELOPMENT.md) file.

## Contributing

We welcome contributions from the community!

If you're interested in improving PromptMage, you can contribute in the following ways:
* **Reporting Bugs**: Submit an issue in our repository, providing a detailed description of the problem and steps to reproduce it.
* **Improve documentation**: If you find any errors or have suggestions for improving the documentation, please submit an issue or a pull request.
* **Fixing Bugs**: Check out our list of open issues and submit a pull request to fix any bugs you find.
* **Feature Requests**: Have ideas on how to make PromptMage better? We'd love to hear from you! Please submit an issue, detailing your suggestions.
* **Pull Requests**: Contributions via pull requests are highly appreciated. Please ensure your code adheres to the coding standards of the project, and submit a pull request with a clear description of your changes.

To ensure a smooth contribution process, please follow these guidelines:
* **create an issue before submitting a pull request** to discuss the changes you'd like to make. This helps us ensure that your contribution aligns with the project's goals and prevents duplicate work.
* **follow the coding standards** of the project. Check the [DEVELOPMENT.md](DEVELOPMENT.md) file for more information.

Make sure to check if your issue or PR has already been fixed or implemented before opening a new one!

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
Original development by [Tobias Sterbak](https://tobiassterbak.com). Copyright (C) 2024.

## Contact
For any inquiries or further information, feel free to reach out at [promptmage@tobiassterbak.com](mailto:promptmage@tobiassterbak.com).

## ❤️ Acknowledgements

This project was supported by

<a href="https://www.media-lab.de/en/programs/media-tech-lab">
    <img src="images/mtl-powered-by.png" width="240" title="Media Tech Lab powered by logo">
</a>