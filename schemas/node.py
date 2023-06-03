from pydantic import BaseModel

from core.magic import AWS_DEFAULT_AMI_ID, AWSInstanceType, NodeState


class NodeBase(BaseModel):
    pass


class NodeCreate(NodeBase):
    state: NodeState
    service_id: int


class Node(NodeBase):
    id: int
    state: NodeState
    service_id: int

    class Config:
        orm_mode = True


class NodeConfig(BaseModel):
    image_id: str = AWS_DEFAULT_AMI_ID
    min_count: int = 1
    max_count: int = 1
    instance_type: AWSInstanceType = AWSInstanceType.t2_micro
    user_data: str = ""
