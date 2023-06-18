from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, Enum, String
from sqlalchemy.orm import relationship

from core.magic import NodeState
from db.base_class import Base


if TYPE_CHECKING:
    from .service import Service  # noqa: F401


class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, index=True)
    state = Column('value', Enum(NodeState))
    service_id = Column(Integer, ForeignKey("services.id"))
    owning_service = relationship("Service", back_populates="nodes")
    public_ip_address = Column(String, nullable=True, default=None)
