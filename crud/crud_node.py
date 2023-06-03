from crud.base import CRUDBase
import models
import schemas


class CRUDNode(CRUDBase[models.Node, schemas.NodeCreate]):
    pass


node = CRUDNode(models.Node)
