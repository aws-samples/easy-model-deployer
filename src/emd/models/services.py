from . import Service
from .utils.constants import ServiceType
from pydantic import BaseModel
from typing import Any
from emd.models import ValueWithDefault


sagemaker_service = Service(
    cfn_parameters={
        "ECRImageURI":"ecr_repo_uri",
        "InstanceType":"instance_type",
        "ModelId": "model_id",
        "ModelTag":"model_tag",
        "FrameWorkType":"framework_type",
        "ServiceType":"service_type",
        "EngineType":"engine_type",
        "Region":"region",
        "MaxCapacity": ValueWithDefault(name="max_capacity",default=1),
        "MinCapacity": ValueWithDefault(name="min_capacity",default=1),
        "AutoScalingTargetValue": ValueWithDefault(name="auto_scaling_target_value",default=10),
        "SageMakerEndpointName": ValueWithDefault(name="sagemaker_endpoint_name",default="Auto-generate"),
        "APIKey": ValueWithDefault(name="api_key",default="")
    },
    name = "Amazon SageMaker AI Real-time inference with OpenAI-Compatible API",
    service_type=ServiceType.SAGEMAKER,
    description="Amazon SageMaker Real-time inference provides low-latency, interactive inference through fully managed endpoints that support autoscaling. It provides an OpenAI-compatible REST API (e.g., /v1/completions) via an Application Load Balancer (ALB).\n(https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html)",
    support_cn_region = True
)

sagemaker_old_service = Service(
    cfn_parameters={
        "ECRImageURI":"ecr_repo_uri",
        "InstanceType":"instance_type",
        "ModelId": "model_id",
        "ModelTag":"model_tag",
        "FrameWorkType":"framework_type",
        "ServiceType":"service_type",
        "EngineType":"engine_type",
        "Region":"region",
        "MaxCapacity": ValueWithDefault(name="max_capacity",default=1),
        "MinCapacity": ValueWithDefault(name="min_capacity",default=1),
        "AutoScalingTargetValue": ValueWithDefault(name="auto_scaling_target_value",default=10),
    },
    name = "Amazon SageMaker AI Real-time inference",
    service_type=ServiceType.SAGEMAKER_OLDER,
    description="Amazon SageMaker Real-time inference provides low-latency, interactive inference through fully managed endpoints that support autoscaling. \n(https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html)",
    support_cn_region = True
)

sagemaker_async_service = Service(
    cfn_parameters={
        "ECRImageURI":"ecr_repo_uri",
        "InstanceType":"instance_type",
        "ModelId": "model_id",
        "S3OutputPath": "s3_output_path",
        # "ExtraParams": "extra_params",
        "ModelTag":"model_tag",
        "FrameWorkType":"framework_type",
        "ServiceType":"service_type",
        "EngineType":"engine_type",
        "Region":"region",
        "MaxCapacity": ValueWithDefault(name="max_capacity",default=1),
        "MinCapacity": ValueWithDefault(name="min_capacity",default=1),
        "AutoScalingTargetValue": ValueWithDefault(name="auto_scaling_target_value",default=10),
        "APIKey": ValueWithDefault(name="api_key",default="")
    },
    name = "Amazon SageMaker AI Asynchronous inference with OpenAI-Compatible API",
    service_type=ServiceType.SAGEMAKER_ASYNC,
    description="Amazon SageMaker Asynchronous Inference queues requests for processing asynchronously, making it suitable for large payloads (up to 1GB) and long processing times (up to one hour), while also enabling cost savings by autoscaling to zero when idle. It provides an OpenAI-compatible REST API (e.g., /v1/completions) via an Application Load Balancer (ALB).\n(https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html)",
    support_cn_region = True
)


ec2_service = Service(
    cfn_parameters={
        "InstanceType":"instance_type",
        "ModelId": "model_id",
        "ModelTag":"model_tag",
        "FrameWorkType":"framework_type",
        "ServiceType":"service_type",
        "EngineType":"engine_type",
        "Region":"region"
    },
    name = "Amazon EC2",
    service_type=ServiceType.EC2,
    description="Amazon Elastic Compute Cloud (Amazon EC2) provides scalable computing capacity in the Amazon Web Services (AWS) cloud.",
    support_cn_region = False,
    need_vpc = True
)

ecs_service = Service(
    cfn_parameters={
        "ECRImageURI":"ecr_repo_uri",
        "InstanceType":"instance_type",
        "ModelId": "model_id",
        "ModelTag":"model_tag",
        "FrameWorkType":"framework_type",
        "ServiceType":"service_type",
        "EngineType":"engine_type",
        "Region": "region",
        "DesiredCapacity": ValueWithDefault(name="desired_capacity",default=1),
        "MaxSize": ValueWithDefault(name="max_size",default=1),
        "VPCID": ValueWithDefault(name="vpc_id",default=""),
        "Subnets": ValueWithDefault(name="subnet_ids",default=""),
        "ContainerCpu": "container_cpu",
        "ContainerMemory": "container_memory",
        "ContainerGpu":"instance_gpu_num",
        "APIKey": ValueWithDefault(name="api_key",default="")
    },
    name = "Amazon ECS with OpenAI-Compatible API",
    service_type=ServiceType.ECS,
    description="Amazon Elastic Container Service is a fully managed service that runs containerized applications in clusters with auto scaling. It provides an OpenAI-compatible REST API (e.g., /v1/completions) via an Application Load Balancer (ALB), enabling integration with AI models for tasks like chatbots or document analysis. (https://docs.aws.amazon.com/AmazonECS/latest/developerguide)",
    support_cn_region = True,
    need_vpc = True
)


local_service = Service(
    cfn_parameters={
        "InstanceType":"instance_type",
        "ModelId": "model_id",
        "ECRImageURI":"ecr_repo_uri",
        "ModelTag":"model_tag",
        "FrameWorkType":"framework_type",
        "ServiceType":"service_type",
        "EngineType":"engine_type",
        "Region":"region"
    },
    name = "Local",
    service_type=ServiceType.LOCAL,
    description="",
    support_cn_region = True
)
