from celery import Celery, Task
from celery.utils.log import get_task_logger
from core.aws import get_ec2_resource

import crud
import schemas
from core.config import settings
from core.magic import (
    AWS_DEFAULT_AMI_ID,
    AWS_SAMPLE_NODE_SCRIPT,
    AWSInstanceType,
    ServiceState,
)
from core.services.base import BaseService
from crud.crud_service import CRUDService
from db.session import SessionLocal
from models import Service
from schemas.common import AWSCredentials
from schemas.node import NodeConfig
from schemas.service import ServiceConfig

celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_BROKER_URL
logger = get_task_logger(__name__)


class BaseServiceTask(Task):
    def __call__(self, *args, **kwargs):
        logger.info(
            "[SERVICE TASK STARTING]: {0.name}[{0.request.id}]".format(self))
        return self.run(*args, **kwargs)


@celery.task(base=BaseServiceTask, name="create_service_task")
def create_service_task(service_id: int) -> bool:
    session = SessionLocal()
    service_db = crud.service.get(db=session, id=service_id)
    service = schemas.Service.from_orm(service_db)
    if service is None:
        raise RuntimeError("Service does not exist")

    # create service with node and service config
    aws_credentials = AWSCredentials.from_settings()
    node_config = NodeConfig()
    service_config = ServiceConfig(name=service.name, service_id=service.id)
    base_service = BaseService(
        aws_credentials=aws_credentials, node_config=node_config, service_config=service_config
    )

    base_service.create()
    session.query(Service).filter(Service.name == service.name).update(
        {"state": ServiceState.running}
    )
    session.commit()
    return True
