from fastapi import APIRouter
from api.endpoints import service


api_router = APIRouter()

api_router.include_router(service.router, prefix="/service", tags=["services"])
