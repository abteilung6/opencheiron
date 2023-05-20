from pydantic import BaseModel


# Shared properties
class ServiceBase(BaseModel):
    name: str


class ServiceCreateRequest(ServiceBase):
    pass


class Service(ServiceBase):
    pass
