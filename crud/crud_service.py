from crud.base import CRUDBase
import models
import schemas


class CRUDService(CRUDBase[models.Service, schemas.ServiceCreate]):
    pass


service = CRUDService(models.Service)
