from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from core.magic import ServiceState
from db.base_class import Base

if TYPE_CHECKING:
    from .node import Node  # noqa: F401


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    state = Column('value', Enum(ServiceState))
    nodes = relationship("Node", back_populates="owning_service")
