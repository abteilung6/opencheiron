from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base_class import Base


if TYPE_CHECKING:
    from .service import Service  # noqa: F401


class KeyPair(Base):
    __tablename__ = "key_pairs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    key_fingerprint = Column(String, nullable=False)
    key_material = Column(String, nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"))
    owning_service = relationship("Service", back_populates="key_pairs")
