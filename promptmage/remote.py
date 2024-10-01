"""This module contains the api for the remote backend of the PromptMage package."""

from pydantic import BaseModel
from slugify import slugify

from fastapi import FastAPI, Path, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from promptmage import RunData, Prompt


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
            self.data_backend.store_data(RunData(**run_data))

        @app.get("/runs/{step_run_id}", tags=["runs"])
        async def get_run(step_run_id: str = Path(...)):
            return self.data_backend.get_data(step_run_id)

        @app.get("/runs", tags=["runs"])
        async def get_all_runs():
            return self.data_backend.get_all_data()

        # Endpoints for the prompt storage backend
        @app.post("/prompts", tags=["prompts"])
        async def store_prompt(prompt: dict):
            self.prompt_backend.store_prompt(Prompt(**prompt))

        @app.put("/prompts", tags=["prompts"])
        async def update_prompt(prompt: dict):
            self.prompt_backend.update_prompt(Prompt(**prompt))

        @app.get("/prompts", tags=["prompts"])
        async def get_prompt(
            prompt_name: str = Query(None),
            version: int = Query(None),
            active: bool = Query(None),
        ):
            return self.prompt_backend.get_prompt(prompt_name, version, active)

        @app.get("/prompts", tags=["prompts"])
        def get_prompts():
            return self.prompt_backend.get_prompts()

        @app.get("/prompts/{prompt_id}", tags=["prompts"])
        async def get_prompt_by_id(prompt_id: str = Path(...)):
            return self.prompt_backend.get_prompt_by_id(prompt_id)

        @app.delete("/prompts/{prompt_id}", tags=["prompts"])
        async def delete_prompt(prompt_id: str = Path(...)):
            self.prompt_backend.delete_prompt(prompt_id)

        return app
