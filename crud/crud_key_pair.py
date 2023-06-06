from crud.base import CRUDBase
import models
import schemas


class CRUDNode(CRUDBase[models.KeyPair, schemas.KeyPairCreate]):
    pass


key_pair = CRUDNode(models.KeyPair)
