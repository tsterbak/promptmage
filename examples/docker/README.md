# PromptMage with Docker Example

This example demonstrates how to use PromptMage with Docker.

## Prerequisites

- Install docker
- Add .env file with the api keys you need. You can use the .env.example file as a template.

## Usage

### Build the Docker image

```bash
docker build -t promptmage-example .
```

### Run the Docker container

```bash
docker run -p 8000:8000 -v $(pwd)/.promptmage:/app/.promptmage --env-file ./.env promptmage-example
```

### Access the API

```bash
http://localhost:8000
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

