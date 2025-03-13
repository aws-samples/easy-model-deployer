import boto3
import time
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


def stop_pipeline_execution(
        model_id:str,
        model_tag:str,
        pipeline_name=CODEPIPELINE_NAME,
        waiting_until_complete=True
    ):
    active_executuion_infos = get_pipeline_active_executions(
        pipeline_name=pipeline_name
    )
    active_executuion_infos_d = {
        Model.get_model_stack_name_prefix(d['model_id'],d['model_tag']):d for d in active_executuion_infos
    }
    cur_uuid = Model.get_model_stack_name_prefix(model_id,model_tag)
    if cur_uuid in active_executuion_infos_d:
        pipeline_execution_id = active_executuion_infos_d[cur_uuid]['pipeline_execution_id']
        client = boto3.client('codepipeline', region_name=get_current_region())
        try:
            client.stop_pipeline_execution(
                pipelineName=pipeline_name,
                pipelineExecutionId=pipeline_execution_id
            )
        except client.exceptions.DuplicatedStopRequestException as e:
            logger.error(e)
        if waiting_until_complete:
            while True:
                execution_info = get_pipeline_execution_info(
                    pipeline_name=pipeline_name,
                    pipeline_execution_id=pipeline_execution_id,
                )
                logger.info(f"pipeline execution status: {execution_info['status']}")
                if execution_info['status'] == 'Stopped':
                    break
                time.sleep(5)
    else:
        logger.error(f"model: {model_id}, model_tag: {model_tag} not found in pipeline executions.")


def destroy_ecs(model_id,model_tag,stack_name):
    cf_client = boto3.client('cloudformation', region_name=get_current_region())
    cf_client.delete_stack(StackName=stack_name)

def destroy(model_id:str,model_tag=MODEL_DEFAULT_TAG,waiting_until_complete=True):
    check_env_stack_exist_and_complete()
    stack_name = Model.get_model_stack_name_prefix(model_id,model_tag=model_tag)
    if not check_stack_exists(stack_name):
        stop_pipeline_execution(model_id,model_tag,waiting_until_complete=waiting_until_complete)
        return

    stack_info = get_stack_info(stack_name)
    parameters = stack_info['parameters']
    if parameters['ServiceType'] == ServiceType.ECS:
        return destroy_ecs(model_id, model_tag,stack_name)

    cf_client = boto3.client('cloudformation', region_name=get_current_region())
    cf_client.delete_stack(StackName=stack_name)

    logger.info(f"Delete stack initiated: {stack_name}")
    # check delete status
    if waiting_until_complete:
        while True:
            status_info = get_destroy_status(stack_name)
            status = status_info['status']
            status_code = status_info['status_code']
            if status_code == 0:
                break
            logger.info(f'stack delete status: {status}')
            time.sleep(5)
        if status == EMD_STACK_NOT_EXISTS_STATUS:
            status = "DELETE_COMPLETED"
        logger.info(f'stack delete status: {status}')
