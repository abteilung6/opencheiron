from pydantic import BaseModel

from core.magic import ServiceState


# Shared properties
class ServiceBase(BaseModel):
    name: str


class ServiceCreateRequest(ServiceBase):
    pass


class Service(ServiceBase):
    id: int
    state: ServiceState

    class Config:
        orm_mode = True
