import uuid

from temporalio.client import Client
from temporalio.worker import Worker
from httpx import AsyncClient

from hello.hello_activity import (
    GreetingWorkflow,
    compose_greeting,
)
from fastapi_app.api import DependencyOverrider, app, temporal_client
import pytest



async def test_fastapi_workflow_without_testclient(client: Client):
    task_queue_name = "hello-activity-task-queue"

    async with Worker(
        client,
        task_queue=task_queue_name,
        workflows=[GreetingWorkflow],
        activities=[compose_greeting],
    ):
        assert "Hello, World!" == await client.execute_workflow(
            GreetingWorkflow.run,
            "World",
            id=str(uuid.uuid4()),
            task_queue=task_queue_name,
        )

async def test_fastapi_workflow_with_testclient(client: Client):
    task_queue_name = "hello-activity-task-queue"
    async def override_dependency():
        return client

    app.dependency_overrides[temporal_client] = override_dependency
    async with Worker(
        client,
        task_queue=task_queue_name,
        workflows=[GreetingWorkflow],
        activities=[compose_greeting],
    ):
        response = test_client.post(
            "/",
        )
        assert response.status_code == 200

async def test_fastapi_workflow_with_dep_override(client: Client):
    task_queue_name = "hello-activity-task-queue"
    with DependencyOverrider(app, overrides={temporal_client: lambda: client}):
        async with Worker(
            client,
            task_queue=task_queue_name,
            workflows=[GreetingWorkflow],
            activities=[compose_greeting],
        ):
            response = test_client.post(
                "/",
            )
            assert response.status_code == 200

@pytest.mark.anyio
async def test_fastapi_workflow_with_deps_async_client(client: Client):
    task_queue_name = "hello-activity-task-queue"
    with DependencyOverrider(app, overrides={temporal_client: lambda: client}):
        async with Worker(
            client,
            task_queue=task_queue_name,
            workflows=[GreetingWorkflow],
            activities=[compose_greeting],
        ):  
            async with AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.post(
                    "/",
                )
            assert response.status_code == 200