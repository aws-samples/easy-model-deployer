import typer
from rich.console import Console
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
import time

from typing import Annotated, Optional
from emd.sdk.status import get_model_status
from rich.table import Table
from emd.utils.decorators import catch_aws_credential_errors,check_emd_env_exist,load_aws_profile
from emd.constants import MODEL_DEFAULT_TAG
from emd.utils.logger_utils import make_layout
from emd.utils.aws_service_utils import get_account_id


app = typer.Typer()
console = Console()
layout = make_layout()


@app.callback(invoke_without_command=True)
@catch_aws_credential_errors
@check_emd_env_exist
@load_aws_profile
def status(
    model_id: Annotated[
        str, typer.Argument(help="Model ID"),
    ]=None,
    model_tag: Annotated[
        str, typer.Argument(help="Model tag")
    ] = MODEL_DEFAULT_TAG,
):
    ret = get_model_status(model_id,model_tag=model_tag)
    inprogress = ret['inprogress']
    completed = ret['completed']

    data = []
    for d in inprogress:
        if d['status'] == "Stopped":
            continue
        data.append({
            "model_id":d['model_id'],
            "model_tag":d['model_tag'],
            "status": f"{d['status']} ({d['stage_name']})",
            "region":d['region'],
            "service_type":d['service_type'],
            "instance_type":d['instance_type'],
            "engine_type":d['engine_type'],
            "framework_type":d['framework_type'],
            "create_time":d['create_time'],
            "outputs":d['outputs'],
            "deploy_version":d['deploy_version']
        })

    for d in completed:
        data.append({
            "model_id":d['model_id'],
            "model_tag":d['model_tag'],
            "status": d['stack_status'],
            "region":d['region'],
            "service_type":d['service_type'],
            "instance_type":d['instance_type'],
            "engine_type":d['engine_type'],
            "framework_type":d['framework_type'],
            "create_time":d['create_time'],
            "outputs":d['outputs'],
            "deploy_version":d['deploy_version']
        })

    account_id = get_account_id()
    table = Table(show_lines=True, expand=True)
    table.add_column("ModelId", justify="left",overflow='fold')
    table.add_column("ModelTag", justify="left",overflow='fold')
    table.add_column("DeployVersion", justify="left",overflow='fold')
    table.add_column("Status", justify="left",overflow='fold')
    table.add_column("Region", justify="left",overflow='fold')
    table.add_column("Account", justify="left",overflow='fold')
    table.add_column("Service", justify="left",overflow='fold')
    table.add_column("Instance", justify="left",overflow='fold')
    table.add_column("Engine", justify="left",overflow='fold')
    table.add_column("Framework", justify="left",overflow='fold')
    table.add_column("CreateTime", justify="left",overflow='fold')
    table.add_column("Outputs", justify="left",overflow='fold')

    # table.field_names = ["model_id", "status"]
    for d in data:
        table.add_row(
            d['model_id'],
            "" if d['model_tag'] == MODEL_DEFAULT_TAG else d['model_tag'],
            d['deploy_version'],
            d['status'],
            d['region'],
            str(account_id),
            d['service_type'],
            d['instance_type'],
            d['engine_type'],
            d['framework_type'],
            d['create_time'],
            d['outputs']
        )
        # table.add_row([d['model_id'], d['status']])
    console.print(table)


if __name__ == "__main__":
    status()
