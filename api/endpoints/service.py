from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import schemas
import crud
from api.deps import get_db
from core.magic import ServiceState
from worker import create_service_task


router = APIRouter()


@router.get("/", response_model=List[schemas.Service])
def list_services(db: Session = Depends(get_db),) -> Any:
    return crud.service.get_multi(db=db)


@router.post("/", response_model=schemas.Service)
def create_service(service_in: schemas.ServiceCreate, db: Session = Depends(get_db)) -> Any:
    service = crud.service.create(db=db, obj_in=schemas.Service(name=service_in.name, state=ServiceState.initialized))
    create_service_task.delay(service.name)
    return service

