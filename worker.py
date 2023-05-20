import time
from celery import Celery


celery = Celery(__name__)
celery.conf.broker_url = "redis://192.168.2.100:6379/0"
celery.conf.result_backend = "redis://192.168.2.100:6379/0"


@celery.task(name="create_task")
def create_task() -> bool:
    time.sleep(5)
    return True
