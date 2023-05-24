from pydantic import BaseModel

from core.magic import ServiceState


# Shared properties
class ServiceBase(BaseModel):
    name: str


class ServiceCreate(ServiceBase):
    pass


class Service(ServiceBase):
    state: ServiceState

    class Config:
        orm_mode = True
