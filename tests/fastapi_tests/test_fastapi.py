import uuid

from temporalio.client import Client
from temporalio.worker import Worker
from fastapi.testclient import TestClient

from hello.hello_activity import (
    GreetingWorkflow,
    compose_greeting,
)
from fastapi_app.api import DependencyOverrider, app, temporal_client

test_client = TestClient(app)

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