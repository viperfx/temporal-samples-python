from typing import Annotated

from temporalio.client import Client
from fastapi import FastAPI
from fastapi import Depends


import typing

from hello.hello_activity import GreetingWorkflow


class DependencyOverrider:
    def __init__(self, app: FastAPI, overrides: typing.Mapping[typing.Callable, typing.Callable]) -> None:
        self.overrides = overrides
        self._app = app
        self._old_overrides = {}

    def __enter__(self):
        for dep, new_dep in self.overrides.items():
            if dep in self._app.dependency_overrides:
                # Save existing overrides
                self._old_overrides[dep] = self._app.dependency_overrides[dep]
            self._app.dependency_overrides[dep] = new_dep
        return self

    def __exit__(self, *args: typing.Any) -> None:
        for dep in self.overrides.keys():
            if dep in self._old_overrides:
                # Restore previous overrides
                self._app.dependency_overrides[dep] = self._old_overrides.pop(dep)
            else:
                # Just delete the entry
                del self._app.dependency_overrides[dep]
                
async def temporal_client() -> Client:
    return await Client.connect("localhost:7233")

TemporalClient = Annotated[Client, Depends(temporal_client)]

app = FastAPI()

@app.post("/")
async def root(client: TemporalClient):
    await client.execute_workflow(
        GreetingWorkflow.run,
        "World",
        id="hello-activity-workflow-id",
        task_queue="hello-activity-task-queue",
    )
    return {"message": "Hello World"}

