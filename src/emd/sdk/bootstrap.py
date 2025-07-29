
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import time
import os
from enum import Enum
import json
from emd.utils.aws_service_utils import get_current_region

from emd.constants import (
    VERSION,
    ENV_STACK_NAME,
    CODEPIPELINE_NAME,
    CODEBUILD_ROLE_NAME_TEMPLATE,
    CODEPIPELINE_ROLE_NAME_TEMPLATE,
    CLOUDFORMATION_ROLE_NAME_TEMPLATE,
    ENV_BUCKET_NAME_PREFIX
)

from emd.utils.upload_pipeline import upload_pipeline_source_to_s3,emd_package_dir
from emd.utils.logger_utils import get_logger
from emd.utils.aws_service_utils import (
    calculate_md5_string,
    get_account_id,
    get_stack_info,
    check_stack_exist_and_complete,
    monitor_stack
)
logger = get_logger(__name__)


# def get_version_md5_value():
#     version_md5_value = calculate_md5_string(
#         f"{VERSION}-{get_account_id()}"
#     )[:8]
#     return version_md5_value


def get_bucket_name(
        bucket_prefix="emd-env-artifactbucket",
        region=None
    ):
    """
    get bucket name
    """
    assert region is not None,region
    # version_md5_value = get_version_md5_value()
    bucket_name = f"{bucket_prefix}-{get_account_id()}-{region}"
    return bucket_name


def create_env_stack(
        region,
        stack_name=ENV_STACK_NAME,
        bucket_name=None,
        bucket_prefix=ENV_BUCKET_NAME_PREFIX,
        pipeline_zip_s3_key=f"{VERSION}/pipeline.zip",
        on_failure = "ROLLBACK",
        force_update = False
    ):
    """
    Args:
        region (_type_): _description_
        stack_name (_type_, optional): _description_. Defaults to ENV_STACK_NAME.
        bucket_name (_type_, optional): _description_. Defaults to None.
        bucket_prefix (str, optional): _description_. Defaults to "emd-env-artifactbucket".

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """
    if check_stack_exist_and_complete(stack_name) and not force_update:
        logger.info(f"env stack: {stack_name} exists...")
        return
    # version_md5_value = get_version_md5_value()
    if bucket_name is None:
        bucket_name = get_bucket_name(
            bucket_prefix=bucket_prefix,
            region=region
        )

    # upload source to s3
    logger.info(f'upload pipeline source to s3://{bucket_name}/{pipeline_zip_s3_key}...')
    pipeline_s3_path = upload_pipeline_source_to_s3(
        bucket_name,
        region,
        s3_key=pipeline_zip_s3_key
    )
    # logger.info(f'pipeline s3 path: {pipeline_s3_path}')

    # create env stack
    cloudformation = boto3.client('cloudformation', region_name=region)
    cfn_template_path = os.path.join(emd_package_dir, "cfn", "codepipeline", "template.yaml")
    with open(cfn_template_path, 'r') as f:
        template_body = f.read()

    stack_params =[
                {'ParameterKey': 'ArtifactBucketName', 'ParameterValue': bucket_name},
                {'ParameterKey': 'ArtifactVersion', 'ParameterValue': VERSION},
                {'ParameterKey': 'PipelineZipS3Key', 'ParameterValue': pipeline_zip_s3_key},
                {'ParameterKey': 'CodepipepineName', 'ParameterValue': CODEPIPELINE_NAME},
                {'ParameterKey': 'CodeBuildRoleName', 'ParameterValue': CODEBUILD_ROLE_NAME_TEMPLATE.format(region=region)},
                {'ParameterKey': 'CodePipelineRoleName', 'ParameterValue': CODEPIPELINE_ROLE_NAME_TEMPLATE.format(region=region)},
                {'ParameterKey': 'CloudFormationRoleName', 'ParameterValue': CLOUDFORMATION_ROLE_NAME_TEMPLATE.format(region=region)}
    ]
    # logger.info(f"boostrap stack params: {json.dumps(stack_params,ensure_ascii=False,indent=2)}")
    def create_stack():
        response = cloudformation.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
            OnFailure=on_failure,
            EnableTerminationProtection=True,
            Parameters=stack_params
        )
        return response

    try:
        response = create_stack()
    except cloudformation.exceptions.AlreadyExistsException:
        stack_info = get_stack_info(stack_name=stack_name)
        stack_status = stack_info['StackStatus']
        if stack_status in ["ROLLBACK_COMPLETE","ROLLBACK_IN_PROGRESS"] or stack_status.endswith("FAILED"):
            logger.info(f"stack_name {stack_name} status:  ROLLBACK_COMPLETE, deleting...")
            cloudformation.delete_stack(StackName=stack_name)
            while True:
                try:
                    response = create_stack()
                    break
                except cloudformation.exceptions.AlreadyExistsException:
                    logger.info(f"stack_name {stack_name} still exists, waiting...")
                    time.sleep(2)
                    continue
        else:
            try:
                response = cloudformation.update_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
                    Parameters=stack_params
                )
            except cloudformation.exceptions.ClientError as e:
                if "No updates" in str(e):
                    logger.info("UpdateStack: No updates are to be performed.")
                    response = get_stack_info(stack_name=stack_name)
                else:
                    raise

    # Track stack events during creation
    # stack_id = response['StackId']
    logger.info(f"Monitoring deployment stack {stack_name}")
    monitor_stack(stack_name)

def bootstrap():
    region = get_current_region()
    bucket_name = get_bucket_name(
                bucket_prefix=ENV_BUCKET_NAME_PREFIX,
                region=region
        )
    create_env_stack(
        region=region,
        stack_name=ENV_STACK_NAME,
        bucket_name=bucket_name,
        force_update=True
    )
