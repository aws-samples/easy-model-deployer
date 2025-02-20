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
        "AutoScalingTargetValue": ValueWithDefault(name="auto_scaling_target_value",default=10)
    },
    name = "Amazon SageMaker AI Real-time inference",
    service_type=ServiceType.SAGEMAKER,
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
        "Region":"region"
    },
    name = "Amazon SageMaker AI Asynchronous inference",
    service_type=ServiceType.SAGEMAKER_ASYNC,
    description="Amazon SageMaker Asynchronous Inference queues requests for processing asynchronously, making it suitable for large payloads (up to 1GB) and long processing times (up to one hour), while also enabling cost savings by autoscaling to zero when idle.\n(https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html)",
    support_cn_region = False
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
        "ContainerCpu": "container_cpu",
        "ContainerMemory": "container_memory",
        "ContainerGpu":"instance_gpu_num"
    },
    name = "Amazon ECS",
    service_type=ServiceType.ECS,
    description="Amazon ECS is a fully managed service that provides scalable and reliable container orchestration for your applications.",
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
