import time
from celery import Celery

from core.magic import ServiceState
from db.session import SessionLocal
from models import Service

celery = Celery(__name__)
celery.conf.broker_url = "redis://192.168.2.100:6379/0"
celery.conf.result_backend = "redis://192.168.2.100:6379/0"


@celery.task(name="create_task")
def create_task(service_name: str) -> bool:
    time.sleep(10)
    session = SessionLocal()
    session.query(Service).filter(Service.name == service_name).update({"state": ServiceState.running})
    session.commit()
    return True
