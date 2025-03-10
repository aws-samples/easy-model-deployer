import json
import os
import time
from typing import Optional

import boto3
import sys

from emd.constants import (
    CODEPIPELINE_NAME,
    ENV_STACK_NAME,
    MODEL_DEFAULT_TAG,
    VERSION,
    LOCAL_REGION
)
from emd.models import Model
from emd.models.utils.constants import FrameworkType, ServiceType,InstanceType
from emd.models.utils.serialize_utils import dump_extra_params
from emd.utils.aws_service_utils import (
    check_cn_region,
    check_quota_availability,
    check_stack_exists,
    get_current_region,
    get_pipeline_active_executions,
)
from emd.utils.logger_utils import get_logger
from emd.utils.upload_pipeline import ziped_pipeline
from emd.utils.aws_service_utils import get_current_region

from .bootstrap import create_env_stack, get_bucket_name
from .status import get_pipeline_execution_status

logger = get_logger(__name__)


def parse_extra_params(extra_params=None):
    if extra_params is None:
        return {}

    if isinstance(extra_params, dict):
        return extra_params

    assert isinstance(extra_params, str), extra_params
    if os.path.exists(extra_params):
        with open(extra_params) as f:
            return json.load(f)

    return json.loads(extra_params)

    # raise ValueError(f"involid extrap_params; {extra_params}")


def prepare_deploy(
    model_id: str,
    model_tag=MODEL_DEFAULT_TAG,
    service_type=None,
    instance_type=None,
    region=None,
):
    model: Model = Model.get_model(model_id)
    model_stack_name = model.get_model_stack_name_prefix(
        model_id, model_tag=model_tag
    )
    # check if model_id is inprogress in pipeline execution
    if check_stack_exists(model_stack_name):
        raise RuntimeError(
            f"A model with the ID: {model_id} and tag: {model_tag} already exists. Kindly use a different tag to proceed."
        )

    client = boto3.client("codepipeline", region_name=region)
    try:
        active_executuion_infos = get_pipeline_active_executions(
            pipeline_name=CODEPIPELINE_NAME,
            client=client,
            filter_stoped=True,
            filter_failed=True,
        )
        model_uid = Model.get_model_stack_name_prefix(model_id, model_tag)
        active_executuion_infos_d = {
            Model.get_model_stack_name_prefix(d["model_id"], d["model_tag"]): d
            for d in active_executuion_infos
        }

        if model_uid in active_executuion_infos_d:
            model_info = active_executuion_infos_d[model_uid]
            raise RuntimeError(
                f"model: {model_info['model_id']},tag: {model_info['model_tag']} is deploying, please wait for it to complete"
            )
    except client.exceptions.PipelineNotFoundException as e:
        pass

    # check quota
    if check_cn_region(region):
        return
    is_quota_sufficient, message = check_quota_availability(
        service_type, instance_type, desired_count=1, region=region
    )
    if not is_quota_sufficient:
        raise RuntimeError(message)


def deploy(
    model_id: str,
    instance_type: str,
    engine_type: str,
    service_type: str,
    framework_type: str = FrameworkType.FASTAPI,
    model_tag=MODEL_DEFAULT_TAG,
    region: Optional[str] = None,
    model_stack_name=None,
    extra_params=None,
    env_stack_on_failure="ROLLBACK",
    force_env_stack_update=False,
    waiting_until_deploy_complete=True,
) -> dict:
    # Check if AWS environment is properly configured
    logger.info("checking if model is exists...")
    assert (
        model_stack_name is None
    ), f"It is currently not supported to custom model stack name."
    region = get_current_region()
    prepare_deploy(
        model_id,
        model_tag=model_tag,
        service_type=service_type,
        instance_type=instance_type,
        region=region,
    )
    # logger.info("Checking AWS environment...")
    extra_params = extra_params or {}
    if model_stack_name is None:
        # stack_name_suffix = random_suffix()
        model_stack_name = (
            f"{Model.get_model_stack_name_prefix(model_id,model_tag=model_tag)}"
        )
    # Check if CloudFormation stack exists for CodePipeline
    cfn = boto3.client("cloudformation", region_name=region)
    bucket_name = get_bucket_name(
        bucket_prefix="emd-env-artifactbucket", region=region
    )
    logger.info(f"bucket: {bucket_name}")
    pipeline_zip_s3_key = f"{VERSION}/pipeline.zip"
    create_env_stack(
        bucket_name=bucket_name,
        stack_name=ENV_STACK_NAME,
        region=region,
        pipeline_zip_s3_key=pipeline_zip_s3_key,
        on_failure=env_stack_on_failure,
        force_update=force_env_stack_update,
    )

    bootstrap_stack = cfn.describe_stacks(StackName=ENV_STACK_NAME)["Stacks"][0]
    # # Get the pipeline name from the bootstrap stack
    pipeline_resources = [
        resource
        for resource in cfn.describe_stack_resources(
            StackName=bootstrap_stack["StackName"]
        )["StackResources"]
        if resource["ResourceType"] == "AWS::CodePipeline::Pipeline"
    ]
    pipeline_name = pipeline_resources[0]["PhysicalResourceId"]
    logger.info("AWS environment is properly configured.")

    model = Model.get_model(model_id)

    # check instance,service,engine
    supported_instances = model.supported_instance_types
    assert (
        instance_type in supported_instances
    ), f"Instance type {instance_type} is not supported for model {model_id}"

    supported_engines = model.supported_engine_types
    assert (
        engine_type in supported_engines
    ), f"Engine type {engine_type} is not supported for model {model_id}"

    supported_services = model.supported_service_types
    assert (
        service_type in supported_services
    ), f"Service type {service_type} is not supported for model {model_id}"

    # Start pipeline execution
    codepipeline = boto3.client("codepipeline", region_name=region)
    # stack_name_suffix = random_suffix()
    extra_params = dump_extra_params(extra_params)
    variables = [
        {"name": "ModelStackName", "value": model_stack_name},
        {"name": "ModelId", "value": model_id},
        {"name": "ModelTag", "value": model_tag},
        {"name": "ServiceType", "value": service_type},
        {"name": "InstanceType", "value": instance_type},
        {"name": "EngineType", "value": engine_type},
        {"name": "ExtraParams", "value": extra_params},
        {"name": "CreateTime", "value": f"{time.time()}"},
        {"name": "FrameworkType", "value": framework_type},
        {"name": "Region", "value": region},
    ]
    # logger.info(
    #     f"start pipeline execution.\nvariables:\n{json.dumps(variables,ensure_ascii=False,indent=2)}"
    # )

    start_deploy_time = time.time()

    response = codepipeline.start_pipeline_execution(
        name=pipeline_name, variables=variables
    )
    logger.info(
        f"Model deployment pipeline execution initiated. Execution ID: {response['pipelineExecutionId']}"
    )
    execution_id = response["pipelineExecutionId"]
    ret = {
        "pipeline_execution_id": response["pipelineExecutionId"],
        "model_stack_name": model_stack_name,
        "model_id": model_id,
        "model_tag": model_tag,
        "service_type": service_type,
        "framework_type": framework_type,
        "instance_type": instance_type,
        "engine_type": engine_type,
        "extra_params": extra_params,
        "model_deploy_start_time": f"{start_deploy_time}",
    }

    is_succeeded = False
    if waiting_until_deploy_complete:
        logger.info(f"monitor stack: {model_stack_name}")
        client = boto3.client("codepipeline", region_name=region)
        while True:
            try:
                status_info = get_pipeline_execution_status(
                    pipeline_execution_id=response["pipelineExecutionId"],
                    region=region
                )
            except client.exceptions.PipelineExecutionNotFoundException as e:
                logger.info("Waiting for pipeline execution to start...")
                time.sleep(10)
                continue
            status = status_info["status"]
            status_code = status_info["status_code"]
            is_succeeded = status_info["is_succeeded"]
            stage_name = status_info.get("stage_name")
            status_summary = status_info.get("status_summary")
            log_info = f"waiting for model: {model_id} (tag: {model_tag}, service: {service_type}, instance: {InstanceType.convert_instance_type(instance_type,service_type)}) deployment pipeline execution to complete. Current status: {status}"
            if status_summary:
                log_info += f", status_summary: {status_summary}"
            if stage_name:
                log_info += f", in stage: {stage_name}"
            # log_info += f", Execution ID: {execution_id}"
            log_info += f", Duration time: {int(time.time() - start_deploy_time)}s"
            logger.info(log_info)
            if status_code == 0:
                break
            time.sleep(10)
        deploy_time = time.time() - start_deploy_time
        ret["model_deploy_elasped_time"] = deploy_time

    if service_type == ServiceType.SAGEMAKER:
        ret["sagemaker_endpoint_name"] = f"{model_stack_name}-endpoint"
        if not waiting_until_deploy_complete or is_succeeded:
            logger.info(
                f"The output sagemaker endpoint name will be: {model_stack_name}-endpoint"
            )

    failed_info = f"Model: {model_id} (tag: {model_tag}) deployment pipeline execution failed. Execution ID: {execution_id},"
    if check_stack_exists(model_stack_name):
        failed_info += f" or watch error logs in stack: {model_stack_name}"
    if waiting_until_deploy_complete and not is_succeeded:
        logger.info(failed_info)

    if waiting_until_deploy_complete and is_succeeded:
        logger.info(
            f"Model: {model_id} (tag: {model_tag}) deployment pipeline execution succeeded. Execution ID: {execution_id}, elapsed time: {ret['model_deploy_elasped_time']}s"
        )
    return ret


def deploy_local(
    model_id: str,
    instance_type: str,
    service_type: str,
    engine_type: str,
    framework_type: str = FrameworkType.FASTAPI,
    model_tag=MODEL_DEFAULT_TAG,
    # region: Optional[str] = None,
    # model_stack_name=None,
    extra_params=None,
    pipeline_zip_local_path=f"/tmp/emd_{VERSION}/pipeline.zip",
    # env_stack_on_failure = "ROLLBACK",
    # force_env_stack_update = False,
    # waiting_until_deploy_complete = True
) -> dict:
    # cp pipeline to tmp
    extra_params = parse_extra_params(extra_params)
    logger.info(f"parsed extra_params: {extra_params}")
    extra_params = dump_extra_params(extra_params or {})
    dir = os.path.dirname(pipeline_zip_local_path)
    os.makedirs(dir, exist_ok=True)
    with open(pipeline_zip_local_path, "wb") as f:
        buffer = ziped_pipeline()
        f.write(buffer.read())

    # unzip the zip
    import zipfile

    with zipfile.ZipFile(pipeline_zip_local_path, "r") as zip_ref:
        zip_ref.extractall(dir)

    # assert os.system(f"chmod -R 777 {dir}") == 0, f"chmod -R 777 {dir} failed"

    pipeline_cmd = (
        f"cd {dir}/pipeline && {sys.executable} pipeline.py "
        f" --model_id {model_id}"
        f" --model_tag {model_tag}"
        f" --instance_type {instance_type}"
        f" --service_type {service_type}"
        f" --backend_type {engine_type}"
        f" --framework_type {framework_type}"
        f" --region '{LOCAL_REGION}'"
        f" --extra_params '{extra_params}'"
    )
    logger.info(f"pipeline cmd: {pipeline_cmd}")
    assert (
        os.system(pipeline_cmd) == 0
    ), f"run pipeline cmd failed: {pipeline_cmd}"
