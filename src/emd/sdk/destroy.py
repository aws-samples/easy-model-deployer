import boto3
import time
from typing import Union, Tuple
from emd.utils.logger_utils import get_logger
from .status import get_destroy_status
from emd.constants import (
    EMD_STACK_NOT_EXISTS_STATUS,
    CODEPIPELINE_NAME,
    MODEL_DEFAULT_TAG
)
from emd.utils.aws_service_utils import (
    check_stack_exists,
    get_pipeline_active_executions,
    get_pipeline_execution_info,
    check_stack_exist_and_complete,
    check_env_stack_exist_and_complete,
    get_stack_info
)
from emd.models.utils.constants import ServiceType
from emd.models import Model
from emd.utils.aws_service_utils import get_current_region

logger = get_logger(__name__)


def parse_model_identifier(model_identifier: str) -> Tuple[str, str]:
    """
    Parse model identifier in format 'model_id/model_tag'

    Args:
        model_identifier: String in format 'model_id/model_tag' or just 'model_id'

    Returns:
        Tuple of (model_id, model_tag)

    Raises:
        ValueError: If format is invalid

    Examples:
        parse_model_identifier('Qwen2.5-0.5B-Instruct/d2') -> ('Qwen2.5-0.5B-Instruct', 'd2')
        parse_model_identifier('Qwen2.5-0.5B-Instruct') -> ('Qwen2.5-0.5B-Instruct', 'dev')
    """
    if not model_identifier or not model_identifier.strip():
        raise ValueError("Model identifier cannot be empty")

    model_identifier = model_identifier.strip()

    if '/' not in model_identifier:
        # Backward compatibility: treat as model_id with default tag
        return model_identifier, MODEL_DEFAULT_TAG

    parts = model_identifier.split('/')
    if len(parts) != 2:
        raise ValueError(
            f"Invalid format: '{model_identifier}'. "
            f"Expected format: 'model_id/model_tag' (e.g., 'Qwen2.5-0.5B-Instruct/d2')"
        )

    model_id, model_tag = parts
    if not model_id.strip():
        raise ValueError("Model ID cannot be empty")
    if not model_tag.strip():
        raise ValueError("Model tag cannot be empty")

    return model_id.strip(), model_tag.strip()


def stop_pipeline_execution(
        model_id: str,
        model_tag: str,
        pipeline_name: str = CODEPIPELINE_NAME,
        waiting_until_complete: bool = True
    ):
    """
    Stop an active pipeline execution for a model.

    Args:
        model_id: Model ID
        model_tag: Model tag
        pipeline_name: Name of the CodePipeline
        waiting_until_complete: Whether to wait for the stop to complete
    """
    logger.info(f"Checking for active pipeline executions for model: {model_id}, tag: {model_tag}")

    active_executuion_infos = get_pipeline_active_executions(
        pipeline_name=pipeline_name
    )
    active_executuion_infos_d = {
        Model.get_model_stack_name_prefix(d['model_id'], d['model_tag']): d
        for d in active_executuion_infos
    }

    cur_uuid = Model.get_model_stack_name_prefix(model_id, model_tag)
    logger.info(f"Looking for pipeline execution with key: {cur_uuid}")

    if cur_uuid in active_executuion_infos_d:
        execution_info = active_executuion_infos_d[cur_uuid]
        pipeline_execution_id = execution_info['pipeline_execution_id']

        logger.info(f"Found active pipeline execution: {pipeline_execution_id}")
        logger.info(f"Current status: {execution_info.get('status', 'Unknown')}")

        client = boto3.client('codepipeline', region_name=get_current_region())
        try:
            client.stop_pipeline_execution(
                pipelineName=pipeline_name,
                pipelineExecutionId=pipeline_execution_id
            )
            logger.info(f"Stop request sent for pipeline execution: {pipeline_execution_id}")
        except client.exceptions.DuplicatedStopRequestException as e:
            logger.warning(f"Stop request already sent for execution {pipeline_execution_id}: {e}")
        except Exception as e:
            logger.error(f"Failed to stop pipeline execution {pipeline_execution_id}: {e}")
            raise

        if waiting_until_complete:
            logger.info("Waiting for pipeline execution to stop...")
            while True:
                execution_info = get_pipeline_execution_info(
                    pipeline_name=pipeline_name,
                    pipeline_execution_id=pipeline_execution_id,
                )
                current_status = execution_info['status']
                logger.info(f"Pipeline execution status: {current_status}")

                if current_status == 'Stopped':
                    logger.info("Pipeline execution stopped successfully")
                    break
                elif current_status in ['Succeeded', 'Failed', 'Cancelled']:
                    logger.info(f"Pipeline execution completed with status: {current_status}")
                    break

                time.sleep(5)
    else:
        logger.warning(f"No active pipeline execution found for model: {model_id}, tag: {model_tag}")
        logger.info(f"Available active executions: {list(active_executuion_infos_d.keys())}")


def destroy_ecs(model_id,model_tag,stack_name):
    cf_client = boto3.client('cloudformation', region_name=get_current_region())
    cf_client.delete_stack(StackName=stack_name)

def destroy(
    model_id: Union[str, None] = None,
    model_tag: str = MODEL_DEFAULT_TAG,
    model_identifier: Union[str, None] = None,
    waiting_until_complete: bool = True
):
    """
    Destroy a model deployment.

    Args:
        model_id: Model ID (legacy format)
        model_tag: Model tag (legacy format)
        model_identifier: Model identifier in 'model_id/model_tag' format (new format)
        waiting_until_complete: Whether to wait for deletion to complete

    Examples:
        # New format (recommended)
        destroy(model_identifier='Qwen2.5-0.5B-Instruct/d2')

        # Legacy format (still supported)
        destroy(model_id='Qwen2.5-0.5B-Instruct', model_tag='d2')

    Raises:
        ValueError: If neither format is provided or format is invalid
    """
    check_env_stack_exist_and_complete()

    # Handle different input formats
    if model_identifier is not None:
        if model_id is not None:
            raise ValueError("Cannot specify both model_identifier and model_id. Use either the new format (model_identifier='model_id/model_tag') or legacy format (model_id='model_id', model_tag='model_tag')")

        # Parse new format
        try:
            model_id, model_tag = parse_model_identifier(model_identifier)
        except ValueError as e:
            logger.error(f"Invalid model identifier format: {e}")
            raise

    elif model_id is not None:
        # Legacy format
        logger.info(f"Using legacy format -> model_id='{model_id}', model_tag='{model_tag}'")
    else:
        raise ValueError("Must specify either model_identifier (new format) or model_id (legacy format)")

    stack_name = Model.get_model_stack_name_prefix(model_id, model_tag=model_tag)

    if not check_stack_exists(stack_name):
        logger.info(f"Stack {stack_name} does not exist, checking for active pipeline executions...")
        stop_pipeline_execution(model_id, model_tag, waiting_until_complete=waiting_until_complete)
        return

    stack_info = get_stack_info(stack_name)
    parameters = stack_info['parameters']
    if parameters['ServiceType'] == ServiceType.ECS:
        logger.info(f"Destroying ECS service for stack: {stack_name}")
        return destroy_ecs(model_id, model_tag, stack_name)

    cf_client = boto3.client('cloudformation', region_name=get_current_region())
    cf_client.delete_stack(StackName=stack_name)

    logger.info(f"CloudFormation stack deletion started: {stack_name}")

    # check delete status
    if waiting_until_complete:
        while True:
            status_info = get_destroy_status(stack_name)
            status = status_info['status']
            status_code = status_info['status_code']
            if status_code == 0:
                break
            logger.info(f'Stack deletion progress: {status}')
            time.sleep(10)

        if status == EMD_STACK_NOT_EXISTS_STATUS:
            status = "DELETE_COMPLETED"
            logger.info("✅ Model deployment successfully deleted - all resources have been removed")
        else:
            logger.info(f'Stack deletion completed with status: {status}')
