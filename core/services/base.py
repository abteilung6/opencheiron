from functools import cached_property
from io import StringIO
import time
import boto3
from celery.utils.log import get_task_logger
import paramiko
from abc import ABC, abstractmethod

from core.magic import NodeState, ServiceState
from db.session import SessionLocal
import crud
import models
import schemas

logger = get_task_logger(__name__)


class BaseService(ABC):
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

    @abstractmethod
    def on_ssh_connection(self, ssh_client: paramiko.SSHClient):
        ...

    def launch(self):
        """Create service with node and service config."""
        self._create_service_key_pairs()
        self._create_security_group()
        self._launch_single_node()

        time.sleep(10)
        ssh_client = self._establish_ssh_connection()

        session = SessionLocal()
        session.query(models.Service).filter(models.Service.name == self.service_config.name).update(
            {
                "state": ServiceState.running,
                "public_ip_address": self.public_ip_address
            }
        )
        session.commit()
        self.on_ssh_connection(ssh_client)

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
        node = crud.node.create(
            db=session, obj_in=schemas.NodeCreate(
                state=NodeState.pending, service_id=self.service_config.service_id)
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
            {
                "public_ip_address": self.public_ip_address,
                "state": NodeState.running
            }
        )
        session.commit()
        logger.info(f'EC2 instance "{instance.id}" has been started')

    def _establish_ssh_connection(self):
        logger.info(
            "Connecting to EC2 instance via %s",
            self.public_ip_address
        )
        session = SessionLocal()
        service_key_pair = session.query(models.KeyPair).filter(
            models.KeyPair.service_id == self.service_config.service_id
        ).first()
        if service_key_pair is None:
            # TODO: handle multiple key pairs
            raise RuntimeError(
                f"No key pair for service id {self.service_config.service_id} found")

        # Emulate file (or file-like) object in order to receive an RSA key
        in_memory_buffer = StringIO(service_key_pair.key_material)
        private_key = paramiko.RSAKey.from_private_key(in_memory_buffer)
        in_memory_buffer.close()

        client = paramiko.SSHClient()
        policy = paramiko.AutoAddPolicy()
        client.set_missing_host_key_policy(policy)

        client.connect(
            self.public_ip_address,
            username="ubuntu", pkey=private_key
        )

        _, _stdout, _ = client.exec_command("whoami")
        logger.info("Connected as %s", _stdout.read())
        return client

    @property
    def service_name(self) -> str:
        return self.service_config.name

    @property
    def security_group_name(self) -> str:
        return f"service-{self.service_name}"

    @property
    def security_group_id(self) -> str:
        return self._security_group_description["GroupId"]

    @property
    def default_vpc_name(self) -> str:
        return self._vpc_description["VpcId"]

    @property
    def public_ip_address(self) -> str:
        return self._instance_description["PublicIpAddress"]

    @property
    def public_dns_name(self) -> str:
        return self._instance_description["PublicDnsName"]

    @cached_property
    def _instance_description(self):
        response = self.ec2_client.describe_instances(
            Filters=[{
                'Name': 'tag:Name',
                'Values': [
                    self.service_name
                ]
            }]
        )
        logger.debug(
            "Cache instance description for service %s",
            self.service_name
        )
        return response["Reservations"][0]["Instances"][0]

    @cached_property
    def _security_group_description(self):
        response = self.ec2_client.describe_security_groups(
            Filters=[
                dict(Name='group-name', Values=[self.security_group_name])
            ]
        )
        logger.debug(
            "Cache security group description for %s",
            self.security_group_name
        )
        return response['SecurityGroups'][0]

    @cached_property
    def _vpc_description(self):
        # TODO: Use a specific VPC for service creation
        response = self.ec2_client.describe_vpcs()
        logger.debug("Cache default vpc description")
        return response["Vpcs"][0]
