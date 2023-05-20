from typing import Any
from fastapi import APIRouter
from schemas import Service, ServiceCreateRequest


router = APIRouter()


@router.post("/", response_model=Service)
def create_service(service_in: ServiceCreateRequest) -> Any:
    return Service(name=service_in.name)
