import boto3

from core.config import settings
from core.magic import AWS_DEFAULT_REGION


def get_ec2_resource():
    return boto3.resource(
        "ec2",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION,
    )
