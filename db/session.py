from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from db.base_class import Base

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
