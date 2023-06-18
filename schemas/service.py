from pydantic import BaseModel

from core.magic import ServiceState


# Shared properties
class ServiceBase(BaseModel):
    name: str


class ServiceCreateRequest(ServiceBase):
    pass


class ServiceCreate(ServiceBase):
    state: ServiceState


class Service(ServiceBase):
    id: int
    name: str
    state: ServiceState
    public_ip_address: str | None

    class Config:
        orm_mode = True


class ServiceConfig(BaseModel):
    name: str
    service_id: int
