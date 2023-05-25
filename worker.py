import logging
import time
from celery import Celery, Task
from celery.utils.log import get_task_logger

from core.config import settings
from core.magic import ServiceState
from db.session import SessionLocal
from models import Service

celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_BROKER_URL
logger = get_task_logger(__name__)


class BaseService(Task):
    def __call__(self, *args, **kwargs):
        logger.info("[SERVICE TASK STARTING]: {0.name}[{0.request.id}]".format(self))
        return self.run(*args, **kwargs)


@celery.task(base=BaseService, name="create_service_task")
def create_service_task(service_name: str) -> bool:
    time.sleep(10)
    session = SessionLocal()
    session.query(Service).filter(Service.name == service_name).update(
        {"state": ServiceState.running}
    )
    session.commit()
    return True
