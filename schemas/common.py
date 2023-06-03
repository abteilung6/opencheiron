from pydantic import BaseModel

from core.config import settings
from core.magic import AWS_DEFAULT_REGION


class AWSCredentials(BaseModel):
    region: str
    aws_access_key_id: str
    aws_secret_access_key: str

    @classmethod
    def from_settings(cls, region: str = AWS_DEFAULT_REGION) -> 'AWSCredentials':
        return cls(region=region, aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
