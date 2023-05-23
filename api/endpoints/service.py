from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
import schemas
from core.magic import ServiceState
from db.session import SessionLocal
from worker import create_task


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.Service)
def create_service(service_in: schemas.ServiceCreateRequest,  db: Session = Depends(get_db)) -> Any:
    db_service = models.Service(name=service_in.name, state=ServiceState.initialized)
    try:
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Service already exists")

    create_task.delay()
    return db_service
