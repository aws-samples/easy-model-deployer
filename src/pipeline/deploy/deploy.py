import time
import os
import subprocess
import logging
import json
import argparse
from emd.models.utils.constants import (
    InstanceType,
    ServiceType,
    EngineType,
    FrameworkType
)
from emd.models import Model, ExecutableConfig

from utils.common import str2bool
from emd.constants import EMD_DEFAULT_CONTAINER_PREFIX, EMD_MODELS_LOCAL_DIR_TEMPLATE
from emd.models import Instance
from emd.utils.logger_utils import get_logger
from emd.utils.accelerator_utils import check_cuda_exists,check_neuron_exists,get_neuron_core_num

logger = get_logger(__name__)

def run(
    execute_model: Model,
    deploy_params: dict,
    region: str,
    role_name: str,
):
    model_id = execute_model.model_id
    model_tag = deploy_params["ModelTag"]
    backend_type = execute_model.executable_config.current_engine.engine_type
    service_type = execute_model.executable_config.current_service.service_type
    instance_type = deploy_params["InstanceType"]
    img_uri = deploy_params["ECRImageURI"]
    if service_type == ServiceType.LOCAL:
        # Run image locally
        logger.info(f"Running {img_uri} image locally")
        aws_access_key_id = (
            subprocess.run(
                "aws configure get aws_access_key_id",
                shell=True,
                stdout=subprocess.PIPE,
            )
            .stdout.decode("utf-8")
            .strip()
        )
        aws_secret_access_key = (
            subprocess.run(
                "aws configure get aws_secret_access_key",
                shell=True,
                stdout=subprocess.PIPE,
            )
            .stdout.decode("utf-8")
            .strip()
        )
        logger.info(f"Running {img_uri} image")
        accelerator_cli_args = ""
        if Instance.check_inf2_instance(instance_type) or check_neuron_exists():
            # instance = Instance.get_instance_from_instance_type(
            #     instance_type
            # )
            neuron_chips_num = get_neuron_core_num()
            # neuron_chips_num = instance.neuron_core_num // 2
            for i in range(neuron_chips_num):
                accelerator_cli_args += f" --device=/dev/neuron{i}"
        elif check_cuda_exists():
            if os.environ.get("CUDA_VISIBLE_DEVICES"):
                gpus_str = f"device={os.environ['CUDA_VISIBLE_DEVICES']}"
            else:
                gpus_str = "all"
            accelerator_cli_args = f"""--gpus '"{gpus_str}"'"""
        else:
            raise RuntimeError("No accelerator found")

        reguar_model_dir = EMD_MODELS_LOCAL_DIR_TEMPLATE.format(model_id=model_id)
        if execute_model.model_files_local_path is not None:
            model_dir = execute_model.model_files_local_path
        else:
            model_dir = reguar_model_dir
        model_dir_abs = os.path.abspath(model_dir)
        model_dir_in_image = f"/{model_dir}"
        container_name = f"{EMD_DEFAULT_CONTAINER_PREFIX}-{model_id.replace('/', '-')}-{int(time.time())}"  # emd-Qwen2.5-72B-Instruct-AWQ-1740116480
        running_cmd = (
            f"docker run --shm-size 1g"
            f" --restart always"  # Always restart in case EC2 restart for patching
            f" --name {container_name}"
            f" -e model_id={model_id}  -e model_tag={model_tag}"
            f" -e MODEL_DIR={model_dir_in_image}"
            f" -e AWS_ACCESS_KEY_ID={aws_access_key_id} -e AWS_SECRET_ACCESS_KEY={aws_secret_access_key}"
            f" -dit {accelerator_cli_args} -v {model_dir_abs}:{model_dir_in_image} -p 8080:8080 {img_uri}" # daemon run with attached logging
            f" && docker logs -f {container_name}"
        )
        logger.info(f"Running {running_cmd}")
        os.system(running_cmd)
    elif service_type == ServiceType.SAGEMAKER:
        # Create SageMaker endpoint
        from service.sagemaker.create_sagemaker_endpoint import (
            get_or_create_role,
            create_sagemaker_endpoint,
        )

        time.sleep(10)
        sagemaker_endpoint_name = (
            model_id.replace("/", "-").replace(".", "-")
            + "-"
            + backend_type
            + "-"
            + time.strftime("%Y-%m-%d-%H-%M-%S")
        )

        role_arn = get_or_create_role(role_name, region)

        create_sagemaker_endpoint(
            region=region,
            instance_type=instance_type,
            role_arn=role_arn,
            image_uri=img_uri,
            endpoint_name=sagemaker_endpoint_name,
            model_id=model_id,
            is_async_deploy=False,
        )
    elif service_type == ServiceType.SAGEMAKER_ASYNC:
        # Create SageMaker endpoint
        s3_output_path = deploy_params.get("S3OutputPath", "")
        from service.sagemaker.create_sagemaker_endpoint import (
            get_or_create_role,
            create_sagemaker_endpoint,
        )
        sagemaker_endpoint_name = (
            model_id.replace("/", "-").replace(".", "-")
            + "-"
            + backend_type
            + "-"
            + time.strftime("%Y-%m-%d-%H-%M-%S")
        )

        role_arn = get_or_create_role(role_name, region)

        create_sagemaker_endpoint(
            region=region,
            instance_type=instance_type,
            role_arn=role_arn,
            image_uri=img_uri,
            endpoint_name=sagemaker_endpoint_name,
            model_id=model_id,
            is_async_deploy=True,
            s3_output_path=s3_output_path,
        )
    else:
        raise ValueError(f"Invalid service type: {service_type}")
