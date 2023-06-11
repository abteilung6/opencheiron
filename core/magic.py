import enum


class ServiceState(enum.Enum):
    initialized = "initialized"
    running = "running"


class NodeState(enum.Enum):
    """A node transitions through different states from the moment we launch it through to its termination."""

    pending = "pending"
    """The node is preparing to enter the running state. 
    An instance enters the pending state when it is launched."""

    running = "running"
    """The node is running and ready for use."""


class AWSInstanceType(enum.Enum):
    """Instance types are named based on their family, generation, additional capabilities, and size.

    The first position of the instance type name indicates the instance family, for example t.
    The second position indicates the instance generation, for example 1.
    The remaining letters before the period indicate additional capabilities, such as instance store volumes.
    See https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-types.html
    """

    t2_micro = "t2.micro"
    """T2 instances are a low-cost, general purpose instance type that provides a baseline level of CPU performance 
    with the ability to burst above the baseline when needed"""


AWS_DEFAULT_REGION = "us-west-2"
#  ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-20230516
AWS_DEFAULT_AMI_ID = "ami-03f65b8614a860c29"
AWS_DEFAULT_AMI_USERNAME = "ubuntu"
AWS_SAMPLE_NODE_SCRIPT = """#!/bin/bash
echo hi
"""
