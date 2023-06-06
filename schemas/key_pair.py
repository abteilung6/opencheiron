from pydantic import BaseModel


class KeyPairBase(BaseModel):
    name: str
    key_fingerprint: str
    key_material: str
    service_id: int


class KeyPairCreate(KeyPairBase):
    pass


class KeyPair(KeyPairBase):
    id: int

    class Config:
        orm_mode = True
