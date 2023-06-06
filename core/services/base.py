import boto3
from typing import Any
from celery.utils.log import get_task_logger

from core.magic import NodeState, ServiceState
from db.session import SessionLocal
import crud
import models
import schemas

logger = get_task_logger(__name__)


class BaseService:
    def __init__(self, aws_credentials: schemas.AWSCredentials, node_config: schemas.NodeConfig, service_config: schemas.ServiceConfig) -> None:
        self.aws_credentials = aws_credentials
        self.node_config = node_config
        self.service_config = service_config
        self.ec2_resource = self._get_ec2_resource()

    def _get_ec2_resource(self) -> Any:
        logger.info("Get EC2 resource")

        return boto3.resource(
            "ec2",
            aws_access_key_id=self.aws_credentials.aws_access_key_id,
            aws_secret_access_key=self.aws_credentials.aws_secret_access_key,
            region_name=self.aws_credentials.region,
        )

    def launch(self):
        """Create service with node and service config."""
        self._create_service_key_pairs()
        self._launch_single_node()

        # [SUCCESS] Service is running
        session = SessionLocal()
        session.query(models.Service).filter(models.Service.name == self.service_config.name).update(
            {"state": ServiceState.running}
        )
        session.commit()

    def _create_service_key_pairs(self) -> None:
        """Amazon EC2 stores the public key and our service saves the private key to the database.
        
        The key pair name is inherited by the service name.
        """
        logger.info("Create EC2 key pairs")

        boto_key_pair = self.ec2_resource.create_key_pair(KeyName=self.service_config.name)

        session = SessionLocal()
        crud.key_pair.create(
            db=session, obj_in=schemas.KeyPairCreate(
                name=self.service_config.name, 
                key_fingerprint=boto_key_pair.key_fingerprint, 
                key_material=boto_key_pair.key_material, 
                service_id=self.service_config.service_id
            )
        )

    def _launch_single_node(self):
        logger.info("Create EC2 instance")

        session = SessionLocal()
        node = crud.node.create(db=session, obj_in=schemas.NodeCreate(
            state=NodeState.pending, service_id=self.service_config.service_id
            )
        )

        instances = self.ec2_resource.create_instances(
            ImageId=self.node_config.image_id,
            MinCount=self.node_config.min_count,
            MaxCount=self.node_config.max_count,
            InstanceType=self.node_config.instance_type.value,
            KeyName=self.service_config.name,
            UserData=self.node_config.user_data,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": self.service_config.name},
                    ],
                },
            ],
        )

        for instance in instances:
            logger.info(
                f'EC2 instance "{instance.id}" has been launched. Wait until running.'
            )
            instance.wait_until_running()
            # [SUCCESS] Node is running
            session = SessionLocal()
            session.query(models.Node).filter(models.Node.id == node.id).update(
                {"state": NodeState.running}
            )
            session.commit()
            logger.info(f'EC2 instance "{instance.id}" has been started')
