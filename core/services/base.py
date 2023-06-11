from functools import cached_property
import boto3
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
        self.ec2_resource = self._get_ec2_resource(aws_credentials)
        self.ec2_client = self._get_ec2_client(aws_credentials)

    @staticmethod
    def _get_ec2_resource(aws_credentials: schemas.AWSCredentials):
        logger.info("Get EC2 resource")
        return boto3.resource(
            "ec2",
            aws_access_key_id=aws_credentials.aws_access_key_id,
            aws_secret_access_key=aws_credentials.aws_secret_access_key,
            region_name=aws_credentials.region,
        )

    @staticmethod
    def _get_ec2_client(aws_credentials: schemas.AWSCredentials):
        logger.info("Get EC2 client")
        return boto3.client(
            "ec2",
            aws_access_key_id=aws_credentials.aws_access_key_id,
            aws_secret_access_key=aws_credentials.aws_secret_access_key,
            region_name=aws_credentials.region,
        )

    def launch(self):
        """Create service with node and service config."""
        self._create_service_key_pairs()
        self._create_security_group()
        self._launch_single_node()

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

        boto_key_pair = self.ec2_resource.create_key_pair(
            KeyName=self.service_config.name)

        session = SessionLocal()
        crud.key_pair.create(
            db=session, obj_in=schemas.KeyPairCreate(
                name=self.service_config.name,
                key_fingerprint=boto_key_pair.key_fingerprint,
                key_material=boto_key_pair.key_material,
                service_id=self.service_config.service_id
            )
        )

    def _create_security_group(self) -> None:
        """An Amazon EC2 security group acts as a virtual firewall that controls the traffic for one or more instances.

        You add rules to each security group to allow traffic to or from its associated instances.
        """
        logger.info("Create security group")
        response = self.ec2_resource.create_security_group(
            GroupName=self.security_group_name, VpcId=self.default_vpc_name, Description=f"Security group for service {self.service_name}"
        )
        logger.info(
            "Security group created [%s, %s]", response.group_id, response.group_name
        )
        logger.info(
            "Create ingress rule for security group %s",
            response.group_id
        )
        # An inbound rule permits instances to receive traffic from the specified IPv4 or IPv6 CIDR address range,
        # or from the instances that are associated with the specified destination security groups.
        response.authorize_ingress(
            GroupName=self.security_group_name, IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=22, ToPort=22,
        )
        logger.info(
            "Ingress rule for security group %s created",
            response.group_id
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
            NetworkInterfaces=[
                {
                    "AssociatePublicIpAddress": True,
                    "DeviceIndex": 0,
                    "Groups": [self.security_group_id]
                }
            ],
        )

        # single node
        instance = instances[0]
        logger.info(
            f'EC2 instance "{instance.id}" has been launched. Wait until running.'
        )
        instance.wait_until_running()
        session = SessionLocal()
        session.query(models.Node).filter(models.Node.id == node.id).update(
            {"state": NodeState.running}
        )
        session.commit()
        logger.info(f'EC2 instance "{instance.id}" has been started')

    @property
    def service_name(self) -> str:
        return self.service_config.name

    @property
    def security_group_name(self) -> str:
        return f"service-{self.service_name}"

    @cached_property
    def security_group_id(self) -> str:
        response = self.ec2_client.describe_security_groups(
            Filters=[
                dict(Name='group-name', Values=[self.security_group_name])
            ]
        )
        _security_group_id = response['SecurityGroups'][0]['GroupId']
        logger.debug("Cache security group id %s", _security_group_id)
        return _security_group_id

    @cached_property
    def default_vpc_name(self) -> str:
        response = self.ec2_client.describe_vpcs()
        _default_vpc_name = response.get('Vpcs', [{}])[0].get('VpcId', '')
        logger.debug("Cache default vpc name %s", _default_vpc_name)
        return _default_vpc_name
