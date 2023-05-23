from sqlalchemy import Column, Integer, String, Enum

from core.magic import ServiceState
from db.base_class import Base


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    state = Column('value', Enum(ServiceState))
