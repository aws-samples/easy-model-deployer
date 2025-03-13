import boto3

from emd.constants import CODEPIPELINE_NAME,MODEL_DEFAULT_TAG
from emd.utils.aws_service_utils import check_stack_status
from emd.models import Model
from emd.utils.aws_service_utils import (
    check_stack_status,
    get_pipeline_active_executions,
    get_model_stacks,
    check_env_stack_exist_and_complete
)
from emd.utils.aws_service_utils import get_account_id
from emd.utils.aws_service_utils import get_current_region
def get_pipeline_execution_status(
        pipeline_execution_id:str,
        pipeline_name:str = CODEPIPELINE_NAME,
        region=None
    ):
    if region is None:
        region = get_current_region()
    client = boto3.client('codepipeline', region_name=region)
    response = client.get_pipeline_execution(
        pipelineName=pipeline_name,
        pipelineExecutionId=pipeline_execution_id
    )
    status = response['pipelineExecution']['status']
    status_summary = response['pipelineExecution'].get('statusSummary',"")
    ret = {
        "status":status,
        "status_code":1,
        "is_succeeded": status == 'Succeeded',
        "stage_name":None,
        "status_summary":status_summary
    }
    if status in ['Stopped','Succeeded','Cancelled',"Failed"]:
        ret['status_code'] = 0

    active_executuion_infos = get_pipeline_active_executions(
        pipeline_name=pipeline_name,
        client=client,
        return_dict=True,
        filter_stoped = False,
        filter_failed = False
    )
    if pipeline_execution_id in active_executuion_infos:
        ret['stage_name'] = active_executuion_infos[pipeline_execution_id]['stage_name']

    return ret


def get_destroy_status(stack_name:str):
    stach_status = check_stack_status(stack_name)
    status = stach_status.status
    if not stach_status.is_exist:
        return {
             "status_code": 0,
             "status": status,
             "is_succeeded":True
        }
    if stach_status.status == "DELETE_FAILED":
        return {
             "status_code": 0,
             "is_succeeded":False,
             "status": status,
        }
    return {
             "status_code": 1,
             "is_succeeded":False,
             "status": status,
        }


def get_model_status(model_id:str=None,model_tag=MODEL_DEFAULT_TAG):
    check_env_stack_exist_and_complete()
    active_executuion_infos = get_pipeline_active_executions(
        pipeline_name=CODEPIPELINE_NAME,
        filter_stoped = False,
        filter_failed = False
    )

    def _get_id(model_id,model_tag):
        return f"{model_id}__{model_tag}"

    active_executuion_infos_d = {
        _get_id(active_executuion_info['model_id'],active_executuion_info['model_tag']):active_executuion_info
        for active_executuion_info in active_executuion_infos
    }

    model_stacks = get_model_stacks()
    model_stacks_d = {
        _get_id(model_stack['model_id'],model_stack['model_tag']):model_stack
        for model_stack in model_stacks
    }

    # deduplication
    uuids = set()
    _model_stacks = []
    _active_executuion_infos = []
    for info in model_stacks:
        uuid = _get_id(info['model_id'],info['model_tag'])
        if uuid in uuids:
            continue
        _model_stacks.append(info)
        uuids.add(uuid)

    for info in active_executuion_infos:
        uuid = _get_id(info['model_id'],info['model_tag'])
        if uuid in uuids:
            continue
        _active_executuion_infos.append(info)
        uuids.add(uuid)

    model_stacks =  _model_stacks
    active_executuion_infos = _active_executuion_infos


    ret = {
        "inprogress":[],
        "completed":[]
    }
    cur_id = _get_id(model_id,model_tag)

    if cur_id in active_executuion_infos_d:
        ret['inprogress'].append(active_executuion_infos_d[cur_id])
        return ret

    if cur_id in model_stacks_d:
        ret['completed'].append(model_stacks_d[cur_id])
        return ret

    if model_id is not None:
        return ret

    ret['inprogress'].extend(active_executuion_infos)
    ret["completed"].extend(model_stacks)

    return ret
