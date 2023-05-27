import enum


class ServiceState(enum.Enum):
    initialized = "initialized"
    running = "running"


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
# TODO: programtically receive the suitable image id
AWS_DEFAULT_AMI_ID = "ami-0ab193018f3e9351b"
AWS_SAMPLE_NODE_SCRIPT = """#!/bin/bash
echo hi
"""
