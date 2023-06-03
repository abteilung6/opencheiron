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
def create_service(service_in: schemas.ServiceCreateRequest, db: Session = Depends(get_db)) -> Any:
    service_orm = crud.service.create(
        db=db, obj_in=schemas.ServiceCreate(
            name=service_in.name, state=ServiceState.initialized)
    )
    service = schemas.Service.from_orm(service_orm)
    create_service_task.delay(service.id)
    return service
