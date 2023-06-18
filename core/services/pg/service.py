import paramiko
from celery.utils.log import get_task_logger

from core.services import BaseService


logger = get_task_logger(__name__)


class PGService(BaseService):

    def on_ssh_connection(self, ssh_client: paramiko.SSHClient):
        """Entry point for service based actions."""
        ...
        self.ssh_client: paramiko.SSHClient = ssh_client
        self.boostrap()

    def boostrap(self):
        logger.info("Download package list from repositories")
        _, _stdout, _ = self.ssh_client.exec_command("sudo apt-get update -y")
        logger.debug(_stdout.read())
