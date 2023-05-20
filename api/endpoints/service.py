from typing import Any
from fastapi import APIRouter
from schemas import Service, ServiceCreateRequest
from worker import create_task

router = APIRouter()


@router.post("/", response_model=Service)
def create_service(service_in: ServiceCreateRequest) -> Any:
    task_id = create_task.delay()
    print(task_id)
    print(task_id.status)
    return Service(name=service_in.name)
