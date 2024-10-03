"""This module contains the api for the remote backend of the PromptMage package."""

from loguru import logger

from fastapi import FastAPI, Path, Query
from fastapi.middleware.cors import CORSMiddleware

from promptmage import RunData, Prompt
from promptmage.exceptions import PromptNotFoundException


class RemoteBackendAPI:

    def __init__(self, url: str, data_backend, prompt_backend):
        self.url = url
        self.data_backend = data_backend
        self.prompt_backend = prompt_backend

    def get_app(self) -> FastAPI:
        """Get an instance of the FastAPI app."""
        app = FastAPI(
            title="PromptMage Remote Backend",
            description="API for the remote backend of PromptMage.",
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/", tags=["root"])
        async def index():
            return {"message": "Welcome to the PromptMage Remote Backend!"}

        # Endpoints for the data storage backend
        @app.post("/runs", tags=["runs"])
        async def store_run(run_data: dict):
            logger.info(f"Storing run data: {run_data}")
            run_data = RunData(**run_data)
            run_data.prompt = Prompt(**run_data.prompt)
            self.data_backend.store_data(run_data)

        @app.get("/runs/{step_run_id}", tags=["runs"])
        async def get_run(step_run_id: str = Path(...)):
            return self.data_backend.get_data(step_run_id)

        @app.get("/runs", tags=["runs"])
        async def get_all_runs():
            return self.data_backend.get_all_data()

        # Endpoints for the prompt storage backend

        @app.post("/prompts", tags=["prompts"])
        async def store_prompt(prompt: dict):
            logger.info(f"Storing prompt: {prompt}")
            self.prompt_backend.store_prompt(Prompt(**prompt))

        @app.put("/prompts", tags=["prompts"])
        async def update_prompt(prompt: dict):
            logger.info(f"Updating prompt: {prompt}")
            self.prompt_backend.update_prompt(Prompt(**prompt))

        @app.get("/prompts/{prompt_name}", tags=["prompts"])
        async def get_prompt(
            prompt_name: str = Path(
                ..., description="The name of the prompt to retrieve"
            ),
            version: int | None = Query(None, description="The version of the prompt"),
            active: bool | None = Query(
                None, description="Whether the prompt is active"
            ),
        ):
            logger.info(f"Retrieving prompt with name: {prompt_name}")
            try:
                return self.prompt_backend.get_prompt(prompt_name, version, active)
            except PromptNotFoundException as e:
                logger.error(
                    f"Prompt with ID {prompt_name} not found, returning an empty prompt."
                )
                # return an empty prompt if the prompt is not found
                return Prompt(
                    name=prompt_name,
                    version=1,
                    system="You are a helpful assistant.",
                    user="",
                    template_vars=[],
                    active=False,
                )

        @app.get("/prompts", tags=["prompts"])
        def get_prompts():
            logger.info("Retrieving all prompts.")
            return self.prompt_backend.get_prompts()

        @app.get("/prompts/id/{prompt_id}", tags=["prompts"])
        async def get_prompt_by_id(
            prompt_id: str = Path(..., description="The ID of the prompt to retrieve")
        ):
            logger.info(f"Retrieving prompt with ID {prompt_id}")
            return self.prompt_backend.get_prompt_by_id(prompt_id)

        @app.delete("/prompts/{prompt_id}", tags=["prompts"])
        async def delete_prompt(prompt_id: str = Path(...)):
            logger.info(f"Deleting prompt with ID: {prompt_id}")
            self.prompt_backend.delete_prompt(prompt_id)

        # Endpoints for the datasets

        @app.get("/datasets/{dataset_id}", tags=["datasets"])
        async def get_dataset(dataset_id: str):
            return self.data_backend.get_dataset(dataset_id)

        @app.get("/datasets", tags=["datasets"])
        async def get_datasets():
            return self.data_backend.get_datasets()

        return app
