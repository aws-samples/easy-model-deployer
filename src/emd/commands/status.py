import typer
from rich.console import Console
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
import time

from typing import Annotated, Optional
from emd.sdk.status import get_model_status
from rich.table import Table
from rich.panel import Panel
from rich.box import Box, SIMPLE, MINIMAL
from emd.utils.decorators import catch_aws_credential_errors,check_emd_env_exist,load_aws_profile
from emd.constants import MODEL_DEFAULT_TAG
from emd.utils.logger_utils import make_layout
from emd.utils.aws_service_utils import get_account_id


app = typer.Typer(pretty_exceptions_enable=False)
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
    ret = get_model_status(model_id, model_tag=model_tag)
    inprogress = ret['inprogress']
    completed = ret['completed']

    data = []
    for d in inprogress:
        if d['status'] == "Stopped":
            continue
        data.append({
            "model_id": d['model_id'],
            "model_tag": d['model_tag'],
            "status": f"{d['status']} ({d['stage_name']})",
            "service_type": d['service_type'],
            "instance_type": d['instance_type'],
            "create_time": d['create_time'],
            "outputs": d['outputs'],
        })

    for d in completed:
        data.append({
            "model_id": d['model_id'],
            "model_tag": d['model_tag'],
            "status": d['stack_status'],
            "service_type": d['service_type'],
            "instance_type": d['instance_type'],
            "create_time": d['create_time'],
            "outputs": d['outputs'],
        })

    account_id = get_account_id()

    # Display each model in its own table box
    for model_data in data:
        # Create a table for the model with a thinner border
        model_table = Table(show_header=False, expand=True)

        # Add a single column for the model name header
        model_table.add_column(justify="center")

        # Add the model name as the first row with bold styling
        model_name = f"{model_data['model_id']}/{model_data['model_tag']}"
        model_table.add_row(model_name, style="bold")

        # Create a nested table for model details
        details_table = Table(show_header=False, box=None, expand=True)
        details_table.add_column(justify="left", style="cyan", width=20)
        details_table.add_column(justify="left", overflow="fold")

        # Add model details as name/value pairs
        details_table.add_row("Status", model_data['status'])
        details_table.add_row("Service Type", model_data['service_type'])
        details_table.add_row("Instance Type", model_data['instance_type'])
        details_table.add_row("Create Time", model_data['create_time'])

        # Parse and add outputs as separate rows
        try:
            # Check if outputs is a string that looks like a dictionary
            if model_data['outputs'] and isinstance(model_data['outputs'], str) and '{' in model_data['outputs']:
                # Try to convert the string to a dictionary
                import ast
                outputs_dict = ast.literal_eval(model_data['outputs'])
                if isinstance(outputs_dict, dict):
                    # Define the order of priority keys
                    priority_keys = ["BaseURL", "Model", "ModelAPIKey"]

                    # First add priority keys if they exist
                    for key in priority_keys:
                        if key in outputs_dict:
                            details_table.add_row(key, str(outputs_dict[key]))

                    # Then add any remaining keys
                    for key, value in outputs_dict.items():
                        if key not in priority_keys:
                            details_table.add_row(key, str(value))
                else:
                    details_table.add_row("Outputs", model_data['outputs'])
            else:
                details_table.add_row("Outputs", model_data['outputs'])
        except (SyntaxError, ValueError):
            # If parsing fails, just show the raw outputs
            details_table.add_row("Outputs", model_data['outputs'])

        # Add the details table as a row in the main table
        model_table.add_row(details_table)

        console.print(model_table)
        console.print()  # Add a blank line between models


if __name__ == "__main__":
    status()
