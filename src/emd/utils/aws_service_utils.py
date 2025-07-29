import datetime
import hashlib
import json
import os
import time
from datetime import timezone

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from emd.constants import (
    EMD_STACK_NOT_EXISTS_STATUS,
    EMD_STACK_NOT_WORKING_STATUS,
    EMD_STACK_OK_STATUS,
    ENV_STACK_NAME,
    MODEL_STACK_NAME_PREFIX,
    STACK_COMPLETE_STATUS_LIST,
)
from emd.models import Service, Model
from emd.models.utils.constants import (
    InstanceType,
    ServiceCode,
    ServiceQuotaCode,
)
from emd.utils.exceptions import EnvStackNotExistError

from .logger_utils import get_logger

logger = get_logger(__name__)


class StackStatus:
    def __init__(self, is_stack_exist: bool, stack_info: dict):
        self.is_stack_exist = is_stack_exist
        self.status_info = stack_info

    @property
    def is_exist(self):
        return self.is_stack_exist

    @property
    def status(self):
        return self.status_info.get("StackStatus", EMD_STACK_NOT_EXISTS_STATUS)


def calculate_md5_string(input_string):
    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode("utf-8"))
    return md5_hash.hexdigest()


def check_aws_environment():
    """
    Check if AWS environment configuration verified.by attempting to access AWS services.
    Raises typer.Exit if AWS is not configured correctly.
    """
    try:
        # Try to create a boto3 client and make a simple API call
        sts = boto3.client("sts", region_name=get_current_region())
        response = sts.get_caller_identity()
        logger.info("AWS environment configuration verified.")
        account_id = response["Account"]
        region = boto3.session.Session().region_name
        logger.info(f"AWS Account: {account_id}\nAWS Region: {region}")
    except (ClientError, NoCredentialsError):
        logger.info(
            "Error: AWS credentials not found or invalid.\nPlease configure your AWS credentials using:\naws configure"
        )


def get_account_id():
    sts_client = boto3.client("sts", region_name=get_current_region())
    account_id = sts_client.get_caller_identity()["Account"]
    return account_id


def create_s3_bucket(bucket_name, region):
    s3 = boto3.client("s3", region_name=region)
    try:
        s3.head_bucket(Bucket=bucket_name)
    except:
        try:
            if region == "us-east-1":
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )
            # Enable versioning on the bucket
            s3.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={"Status": "Enabled"},
            )
        except (s3.exceptions.BucketAlreadyOwnedByYou,):
            logger.info(f"bucket: {bucket_name} exists")
        except Exception as e:
            raise


def get_role_create_template(
    role_name: str, services_to_assume: list[str], manage_policy_arns: list[str]
):
    role_create_template = {
        "Type": "AWS::IAM::Role",
        "Properties": {
            "RoleName": role_name,
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": service},
                        "Action": "sts:AssumeRole",
                    }
                    for service in services_to_assume
                ],
            },
            "ManagedPolicyArns": manage_policy_arns,
        },
    }
    return role_create_template


def get_stack_info(stack_name):
    cf = boto3.client("cloudformation", region_name=get_current_region())
    stack_info = cf.describe_stacks(StackName=stack_name)["Stacks"][0]
    parameters = {}
    for parameter in stack_info["Parameters"]:
        parameters[parameter["ParameterKey"]] = parameter["ParameterValue"]
    stack_info["parameters"] = parameters
    return stack_info


def check_stack_exists(stack_name):
    try:
        cf = boto3.client("cloudformation", region_name=get_current_region())
        cf.describe_stacks(StackName=stack_name)
        return True
    except ClientError as e:
        if e.response["Error"][
            "Code"
        ] == "ValidationError" and "does not exist" in str(e):
            return False
        else:
            raise


def check_stack_status(stack_name) -> StackStatus:
    is_stack_exist = True
    stack_info = {}
    try:
        cf = boto3.client("cloudformation", region_name=get_current_region())
        stack_info = cf.describe_stacks(StackName=stack_name)["Stacks"][0]
    except ClientError as e:
        if e.response["Error"][
            "Code"
        ] == "ValidationError" and "does not exist" in str(e):
            is_stack_exist = False
        else:
            raise
    return StackStatus(is_stack_exist=is_stack_exist, stack_info=stack_info)


def batch_check_stack_status(stack_names: list) -> dict:
    """
    Check status of multiple CloudFormation stacks in a single API call.

    This is a performance optimization to avoid individual stack checks.

    Args:
        stack_names: List of stack names to check

    Returns:
        dict: Dictionary mapping stack names to StackStatus objects
    """
    if not stack_names:
        return {}

    cf = boto3.client("cloudformation", region_name=get_current_region())
    stack_statuses = {}

    try:
        # Use describe_stacks with no specific stack name to get all stacks
        paginator = cf.get_paginator('describe_stacks')
        all_stacks = {}

        for page in paginator.paginate():
            for stack in page['Stacks']:
                all_stacks[stack['StackName']] = stack

        # Check each requested stack
        for stack_name in stack_names:
            if stack_name in all_stacks:
                stack_info = all_stacks[stack_name]
                stack_statuses[stack_name] = StackStatus(
                    is_stack_exist=True,
                    stack_info=stack_info
                )
            else:
                stack_statuses[stack_name] = StackStatus(
                    is_stack_exist=False,
                    stack_info={}
                )

    except Exception as e:
        logger.error(f"Error in batch stack check: {e}")
        # Fallback to individual checks on error
        for stack_name in stack_names:
            try:
                stack_statuses[stack_name] = check_stack_status(stack_name)
            except Exception as individual_error:
                logger.error(f"Error checking individual stack {stack_name}: {individual_error}")
                stack_statuses[stack_name] = StackStatus(is_stack_exist=False, stack_info={})

    return stack_statuses


def get_pipeline_stages(pipeline_name: str) -> list[str]:
    client = boto3.client("codepipeline", region_name=get_current_region())
    response = client.get_pipeline_state(name=pipeline_name)
    stages = [i["stageName"] for i in response["stageStates"]]
    return stages


def get_pipeline_execution_info(
    pipeline_name: str, pipeline_execution_id: str, client=None
):

    client = client or boto3.client("codepipeline", region_name=get_current_region())
    execution_info = client.get_pipeline_execution(
        pipelineName=pipeline_name, pipelineExecutionId=pipeline_execution_id
    )["pipelineExecution"]
    return execution_info


def _find_stage_for_execution_via_actions_utils(pipeline_name: str, execution_id: str, client) -> str:
    """
    Find the current/failed stage for a specific pipeline execution using list_action_executions.

    This is a utility version of the function from status.py for use in aws_service_utils.py
    """
    try:
        response = client.list_action_executions(
            pipelineName=pipeline_name,
            filter={
                'pipelineExecutionId': execution_id
            }
        )

        action_executions = response.get('actionExecutionDetails', [])
        logger.debug(f"Found {len(action_executions)} action executions for {execution_id}")

        if not action_executions:
            return "Unknown"

        # Find the stage where execution is currently running or failed
        current_stage = "Unknown"

        # Look for failed or in-progress actions first (these indicate current stage)
        for action_exec in action_executions:
            stage_name = action_exec.get('stageName', 'Unknown')
            status = action_exec.get('status', 'Unknown')

            # If we find a failed or in-progress action, that's the current stage
            if status in ['Failed', 'InProgress', 'Stopping']:
                current_stage = stage_name
                logger.debug(f"Found current/failed stage: {stage_name} (status: {status})")
                break

        # If no failed/in-progress actions, find the last stage (for completed executions)
        if current_stage == "Unknown" and action_executions:
            # Get all unique stages and find the last one in pipeline order
            stages_found = []
            for action_exec in action_executions:
                stage_name = action_exec.get('stageName', 'Unknown')
                if stage_name not in stages_found:
                    stages_found.append(stage_name)

            # For completed executions, return the last stage
            if stages_found:
                current_stage = stages_found[-1]  # Last stage in the list
                logger.debug(f"Execution completed, using last stage: {current_stage}")

        return current_stage

    except Exception as e:
        logger.debug(f"Error getting stage via action executions for {execution_id}: {e}")
        return "Unknown"


def get_pipeline_active_executions(
    pipeline_name: str,
    client=None,
    return_dict=False,
    filter_stoped=True,
    filter_failed=True,
) -> list[dict]:
    client = client or boto3.client("codepipeline", region_name=get_current_region())

    try:
        # Use list_pipeline_executions to get ALL executions (better for PARALLEL mode)
        response = client.list_pipeline_executions(pipelineName=pipeline_name)
        all_executions = response.get("pipelineExecutionSummaries", [])

        # Get additional pages if needed
        while "nextToken" in response:
            response = client.list_pipeline_executions(
                pipelineName=pipeline_name,
                nextToken=response["nextToken"]
            )
            all_executions.extend(response.get("pipelineExecutionSummaries", []))

    except client.exceptions.PipelineNotFoundException:
        raise EnvStackNotExistError

    # Filter for active executions
    active_executuion_infos = []
    status_filter = ["Stopping", "InProgress", "Stopped", "Failed"]
    if filter_stoped:
        status_filter.remove("Stopped")
    if filter_failed:
        status_filter.remove("Failed")

    # Get pipeline state for stage information (fallback method)
    try:
        pipeline_state = client.get_pipeline_state(name=pipeline_name)
        stage_states = pipeline_state["stageStates"]
    except Exception as e:
        logger.warning(f"Could not get pipeline state: {e}")
        stage_states = []

    # Process each execution
    for execution_summary in all_executions:
        execution_status = execution_summary["status"]
        execution_id = execution_summary["pipelineExecutionId"]

        # Skip if not in our status filter
        if execution_status not in status_filter:
            continue

        try:
            # Get detailed execution info
            execution_info = get_pipeline_execution_info(
                pipeline_name=pipeline_name,
                pipeline_execution_id=execution_id,
                client=client,
            )

            # Extract variables
            variables = execution_info.get("variables", [])
            variables_d = {
                variable["name"]: variable["resolvedValue"]
                for variable in variables
            }

            # Skip if missing required variables
            if "ModelId" not in variables_d or "CreateTime" not in variables_d:
                continue

            create_timestamp = float(variables_d["CreateTime"])
            create_time = (
                datetime.datetime.fromtimestamp(create_timestamp)
                .replace(tzinfo=timezone.utc)
                .strftime("%Y-%m-%d %H:%M:%S %Z")
            )

            # Find current stage for this execution - IMPROVED APPROACH
            # First try the action-based approach (works for all execution states)
            current_stage = _find_stage_for_execution_via_actions_utils(
                pipeline_name, execution_id, client
            )

            # If action-based approach fails, fall back to pipeline state approach
            if current_stage == "Unknown":
                logger.debug(f"Action-based stage detection failed for {execution_id}, trying pipeline state")

                for stage_state in stage_states:
                    # Check if this execution is in this stage
                    stage_execution_ids = []

                    # Check inbound executions
                    stage_execution_ids.extend([
                        d["pipelineExecutionId"] for d in stage_state.get("inboundExecutions", [])
                    ])

                    # Check latest execution
                    latest_execution = stage_state.get("latestExecution", {})
                    if latest_execution and latest_execution.get("pipelineExecutionId"):
                        stage_execution_ids.append(latest_execution["pipelineExecutionId"])

                    # Check action states for parallel executions
                    for action_state in stage_state.get("actionStates", []):
                        latest_action = action_state.get("latestExecution", {})
                        if latest_action and latest_action.get("pipelineExecutionId"):
                            stage_execution_ids.append(latest_action["pipelineExecutionId"])

                    if execution_id in stage_execution_ids:
                        current_stage = stage_state["stageName"]
                        logger.debug(f"Found stage via pipeline state: {current_stage}")
                        break

            active_executuion_infos.append(
                {
                    "stage_name": current_stage,
                    "status": execution_status,
                    "pipeline_execution_id": execution_id,
                    "model_id": variables_d["ModelId"],
                    "model_tag": variables_d["ModelTag"],
                    "region": variables_d.get("Region", ""),
                    "create_time": create_time,
                    "execution_info": execution_info,
                    "instance_type": InstanceType.convert_instance_type(
                        variables_d["InstanceType"], variables_d["ServiceType"]
                    ),
                    "engine_type": variables_d["EngineType"],
                    "service_type": Service.get_service_from_service_type(
                        variables_d["ServiceType"]
                    ).name,
                    "framework_type": variables_d["FrameworkType"],
                    "outputs": "",
                    "deploy_version": variables_d.get("DeployVersion", ""),
                }
            )

        except Exception as e:
            logger.warning(f"Error processing execution {execution_id}: {e}")
            continue

    if return_dict:
        return {
            active_executuion_info[
                "pipeline_execution_id"
            ]: active_executuion_info
            for active_executuion_info in active_executuion_infos
        }
    return active_executuion_infos


def get_model_stacks():
    cf = boto3.client("cloudformation", region_name=get_current_region())
    stacks = cf.list_stacks(
        StackStatusFilter=[
            "CREATE_COMPLETE",
            "UPDATE_COMPLETE",
            "ROLLBACK_COMPLETE",
            "DELETE_IN_PROGRESS",
        ]
    )["StackSummaries"]
    model_stacks = []
    for stack in stacks:
        stack_name = stack["StackName"]
        if stack_name.startswith(MODEL_STACK_NAME_PREFIX):
            status_info = cf.describe_stacks(StackName=stack_name)["Stacks"][0]
            outputs = status_info["Parameters"]
            outputs_d = {
                output["ParameterKey"]: output["ParameterValue"]
                for output in outputs
            }

            outputs_d["model_id"] = outputs_d.pop("ModelId")
            outputs_d["model_tag"] = outputs_d.pop("ModelTag")
            outputs_d["stack_name"] = stack_name
            outputs_d["stack_status"] = status_info["StackStatus"]
            outputs_d["region"] = outputs_d.get("Region", "")
            aware_dt = (
                status_info["CreationTime"]
                .replace(tzinfo=timezone.utc)
                .strftime("%Y-%m-%d %H:%M:%S %Z")
            )
            outputs_d["create_time"] = aware_dt
            outputs_d["instance_type"] = outputs_d["InstanceType"]
            outputs_d["framework_type"] = outputs_d["FrameWorkType"]
            outputs_d["service_type"] = Service.get_service_from_service_type(
                outputs_d["ServiceType"]
            ).name
            outputs_d["engine_type"] = outputs_d["EngineType"]
            stack_output_d = {
                output["OutputKey"]: output["OutputValue"]
                for output in status_info.get("Outputs", [])
            }
            outputs_d["outputs"] = str(stack_output_d)

            if outputs_d["stack_status"] == "ROLLBACK_COMPLETE":
                # find failed event
                response = cf.describe_stack_events(StackName=stack_name)
                stack_events = response["StackEvents"]
                for event in stack_events:
                    if event["ResourceStatus"] == "CREATE_FAILED":
                        resource_status_reason = event["ResourceStatusReason"]
                        outputs_d["stack_status"] = (
                            f"{outputs_d['stack_status']}\n{resource_status_reason}"
                        )
            model_stacks.append(outputs_d)
    return model_stacks


def get_model_stack_info(model_stack_name: str):
    cf = boto3.client("cloudformation", region_name=get_current_region())
    stack_info = cf.describe_stacks(StackName=model_stack_name)["Stacks"][0]
    return stack_info


def s3_bucket_version(bucket, s3_key):
    s3_client = boto3.client("s3", region_name=get_current_region())
    version_id: str = s3_client.head_object(Bucket=bucket, Key=s3_key)[
        "VersionId"
    ]
    return version_id


def check_stack_exist_and_complete(stack_name: str):
    client = boto3.client("cloudformation", region_name=get_current_region())
    try:
        response = client.describe_stacks(StackName=stack_name)
        stack_status = response["Stacks"][0]["StackStatus"]
        return stack_status in ["CREATE_COMPLETE", "UPDATE_COMPLETE"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "ValidationError":
            return False
        else:
            raise


def monitor_stack(stack_name):
    """

    Args:
        stack_name (_type_): _description_
    """
    response = get_stack_info(stack_name=stack_name)
    stack_id = response["StackId"]
    seen_events = set()
    cloudformation = boto3.client("cloudformation", region_name=get_current_region())
    # Determine if this is a create or update operation
    while True:
        events = cloudformation.describe_stack_events(StackName=stack_id)[
            "StackEvents"
        ]
        # Process events in reverse order (oldest first)
        for event in reversed(events):
            event_id = event["EventId"]
            if event_id not in seen_events:
                seen_events.add(event_id)
                # Format and print the event
                timestamp = event["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                resource_status = event["ResourceStatus"]
                logical_id = event["LogicalResourceId"]

                logger.info(f"{timestamp} - {logical_id}: {resource_status}")
                if event.get("ResourceStatusReason"):
                    logger.info(f"Reason: {event['ResourceStatusReason']}")

        # Check if stack creation is complete or failed
        stack = cloudformation.describe_stacks(StackName=stack_id)["Stacks"][0]
        if stack["StackStatus"] not in [
            "CREATE_IN_PROGRESS",
            "UPDATE_IN_PROGRESS",
            "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
        ]:
            break
        time.sleep(2)
    # Final status check
    if stack["StackStatus"] not in ["CREATE_COMPLETE", "UPDATE_COMPLETE"]:
        raise RuntimeError(
            f"Stack: {stack_name} creation failed with status: {stack['StackStatus']}"
        )
    else:
        logger.info(
            f"stack: {stack_name} compleated with status:  {stack['StackStatus']}"
        )


def monitor_pipeline(pipeline_name, pipeline_execution_id):
    client = boto3.client("codepipeline", region_name=get_current_region())
    while True:
        response = client.get_pipeline_state(name=pipeline_name)
        for stage in response["stageStates"]:
            stage_name = stage["stageName"]
            status = stage["actionStates"][0]["latestExecution"]["status"]
            logger.info(f"{stage_name}: {status}")
        if (
            response["stageStates"][-1]["actionStates"][0]["latestExecution"][
                "status"
            ]
            == "Succeeded"
        ):
            break
        time.sleep(2)
    logger.info(f"pipeline: {pipeline_name} compleated with status:  {status}")


def check_env_stack_exist_and_complete():
    if not check_stack_exist_and_complete(ENV_STACK_NAME):
        raise EnvStackNotExistError


def get_sagemaker_instance_quota(instance_type: str) -> float:
    """
    Get the SageMaker quota for a specific instance type.

    Args:
        instance_type (str): The instance type (e.g., 'g5.xlarge')

    Returns:
        float: The quota value for the instance type

    Raises:
        ValueError: If the instance type doesn't have a corresponding quota code
        ClientError: If there's an error calling AWS Service Quotas
    """
    service_quota_client = boto3.client("service-quotas", region_name=get_current_region())

    quota_code = ServiceQuotaCode.get_service_quota_code(instance_type)
    response = service_quota_client.get_service_quota(
        ServiceCode=ServiceCode.SAGEMAKER, QuotaCode=quota_code
    )

    service_quota_value = response["Quota"]["Value"]

    return int(service_quota_value)


def get_sagemaker_instance_count_by_type(instance_type: str):
    """
    Get the total number of instances currently running for a specific instance type.

    Args:
        instance_type (str): The AWS instance type (e.g., 'g5.xlarge')

    Returns:
        int: Total number of instances of the specified type
        list: List of endpoint names using this instance type
    """
    # Initialize SageMaker client
    sagemaker_client = boto3.client("sagemaker", region_name=get_current_region())

    sagemaker_instance_type = InstanceType.convert_instance_type_to_sagemaker(
        instance_type
    )

    # Get list of all endpoints with pagination
    endpoints = []
    paginator = sagemaker_client.get_paginator("list_endpoints")
    for page in paginator.paginate():
        endpoints.extend(page["Endpoints"])

    total_instances = 0
    endpoint_names = []

    # Iterate through each endpoint
    for endpoint in endpoints:
        endpoint_details = sagemaker_client.describe_endpoint(
            EndpointName=endpoint["EndpointName"]
        )
        if endpoint_details["EndpointStatus"] != "InService":
            continue

        # Get endpoint configuration details
        endpoint_config = sagemaker_client.describe_endpoint_config(
            EndpointConfigName=endpoint_details["EndpointConfigName"]
        )
        # Get instance type and count from production variants
        current_instance_type = endpoint_config["ProductionVariants"][0][
            "InstanceType"
        ]
        current_instance_count = endpoint_details["ProductionVariants"][0][
            "CurrentInstanceCount"
        ]

        # If this endpoint uses the requested instance type, add to our counts
        if current_instance_type == sagemaker_instance_type:
            total_instances += current_instance_count
            endpoint_names.append(endpoint["EndpointName"])

    return total_instances, endpoint_names


def check_sagemaker_instance_quota_availability(
    instance_type: str, desired_count: int = 1, region: str = None
):
    """
    Check if deploying new SageMaker instances would exceed the service quota.

    Args:
        instance_type (str): The instance type to check (e.g., 'g5.xlarge')
        desired_count (int): Number of instances to be deployed

    Returns:
        tuple[bool, str]: (True if deployment is possible, explanation message)
    """
    try:
        # Get current quota limit
        # If in china region, set a default high quota value since we can't fetch it
        if region in ["cn-north-1", "cn-northwest-1"]:
            quota_limit = (
                100  # Set a reasonable default quota for China regions
            )
        else:
            quota_limit = get_sagemaker_instance_quota(instance_type)

        # Get current instance usage
        current_usage, _ = get_sagemaker_instance_count_by_type(instance_type)

        # Calculate if we have enough capacity
        remaining_quota = quota_limit - current_usage
        is_quota_sufficient = remaining_quota >= desired_count

        message = f"Instance type {instance_type} has {remaining_quota} instances available (limit: {quota_limit}, current usage: {current_usage}, requested: {desired_count})"

        if not is_quota_sufficient:
            message += f". Deployment would exceed quota by {desired_count - remaining_quota} instances"

        return is_quota_sufficient, message

    except Exception as e:
        return False, f"Error checking quota availability: {str(e)}"


def check_quota_availability(
    service_type: str,
    instance_type: str,
    desired_count: int = 1,
    region: str = None,
):
    if service_type == ServiceCode.SAGEMAKER:
        return check_sagemaker_instance_quota_availability(
            instance_type, desired_count, region
        )
    else:
        return True, f"Quota check for {service_type} is not supported yet."


def check_cn_region(region: str):
    return region.startswith("cn")


def get_current_region():
    return os.environ.get("AWS_REGION") or boto3.session.Session().region_name


def get_aws_account_id():
    sts = boto3.client("sts", region_name=get_current_region())
    response = sts.get_caller_identity()
    account_id = response["Account"]
    return account_id
