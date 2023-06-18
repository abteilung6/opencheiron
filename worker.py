from celery import Celery, Task
from celery.utils.log import get_task_logger

import crud
import models
import schemas
from core.config import settings
from core.magic import ServiceState
from core.services import PGService
from db.session import SessionLocal

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
    aws_credentials = schemas.AWSCredentials.from_settings()
    node_config = schemas.NodeConfig()
    service_config = schemas.ServiceConfig(
        name=service.name, service_id=service.id)
    base_service = PGService(
        aws_credentials=aws_credentials, node_config=node_config, service_config=service_config
    )
    base_service.launch()
    return True
