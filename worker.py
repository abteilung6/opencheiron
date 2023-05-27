from celery import Celery, Task
from celery.utils.log import get_task_logger
from core.aws import get_ec2_resource

from core.config import settings
from core.magic import (
    AWS_DEFAULT_AMI_ID,
    AWS_SAMPLE_NODE_SCRIPT,
    AWSInstanceType,
    ServiceState,
)
from db.session import SessionLocal
from models import Service

celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_BROKER_URL
logger = get_task_logger(__name__)


class BaseServiceTask(Task):
    def __call__(self, *args, **kwargs):
        logger.info("[SERVICE TASK STARTING]: {0.name}[{0.request.id}]".format(self))
        return self.run(*args, **kwargs)


@celery.task(base=BaseServiceTask, name="create_service_task")
def create_service_task(service_name: str) -> bool:
    logger.info("Receive EC2 resource")
    ec2_resource = get_ec2_resource()

    logger.info("Launch EC2 instance")
    instances = ec2_resource.create_instances(
        ImageId=AWS_DEFAULT_AMI_ID,
        MinCount=1,
        MaxCount=1,
        InstanceType=AWSInstanceType.t2_micro.value,
        UserData=AWS_SAMPLE_NODE_SCRIPT,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": service_name},
                ],
            },
        ],
    )

    for instance in instances:
        logger.info(
            f'EC2 instance "{instance.id}" has been launched. Wait until running.'
        )
        instance.wait_until_running()
        logger.info(f'EC2 instance "{instance.id}" has been started')

    # Update management db
    session = SessionLocal()
    session.query(Service).filter(Service.name == service_name).update(
        {"state": ServiceState.running}
    )
    session.commit()
    return True
