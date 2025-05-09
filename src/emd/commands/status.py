from typing import Annotated

import typer
from emd.constants import MODEL_DEFAULT_TAG
from emd.sdk.status import get_model_status
from emd.utils.aws_service_utils import get_account_id
from emd.utils.decorators import catch_aws_credential_errors, check_emd_env_exist, load_aws_profile
from emd.utils.logger_utils import make_layout
from rich.console import Console
from rich.table import Table

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

    # Check if there are any models to display
    if not data:
        console.print("No models found.")
        return

    # Extract the base URL from the first model that has it
    base_url = None
    for model_data in data:
        try:
            outputs = model_data.get('outputs', '')
            if outputs and isinstance(outputs, str) and '{' in outputs:
                import ast
                outputs_dict = ast.literal_eval(outputs)
                if isinstance(outputs_dict, dict) and "BaseURL" in outputs_dict:
                    base_url = outputs_dict["BaseURL"]
                    break
        except (SyntaxError, ValueError):
            continue

    # Display the Models section
    console.print("\nModels", style="bold")

    # Create a custom box style without vertical lines

    # Create a single table for all models with normal horizontal lines but no vertical lines
    models_table = Table(show_header=False, expand=True)

    # Add two columns for name/value pairs
    models_table.add_column(justify="left", style="cyan", width=22)
    models_table.add_column(justify="left", overflow="fold")

    # Add each model to the table
    for model_data in data:
        # Add model name as a name/value pair with bold styling
        model_name = f"{model_data['model_id']}/{model_data['model_tag']}"
        models_table.add_row("Model ID", model_name, style="bold")

        # Add model details as name/value pairs (skip empty fields)
        if model_data['status']:
            models_table.add_row("Status", model_data['status'])
        if model_data['service_type']:
            models_table.add_row("Service Type", model_data['service_type'])
        if model_data['instance_type']:
            models_table.add_row("Instance Type", model_data['instance_type'])
        if model_data['create_time']:
            models_table.add_row("Create Time", model_data['create_time'])

        # Parse and add outputs as separate rows (excluding BaseURL since it's shown in the Base URL section)
        try:
            # Check if outputs is a string that looks like a dictionary and is not empty
            outputs = model_data.get('outputs', '')
            if outputs and isinstance(outputs, str) and '{' in outputs and outputs != '{}':
                # Try to convert the string to a dictionary
                import ast
                outputs_dict = ast.literal_eval(outputs)
                if isinstance(outputs_dict, dict) and outputs_dict:  # Check if dict is not empty
                    # Define the order of priority keys (excluding BaseURL and Model)
                    priority_keys = ["ModelAPIKey"]

                    # First add priority keys if they exist
                    for key in priority_keys:
                        if key in outputs_dict and outputs_dict[key]:  # Check if value is not empty
                            # Change the display name of ModelAPIKey to "Query Model API Key"
                            display_name = "Query Model API Key" if key == "ModelAPIKey" else key
                            models_table.add_row(display_name, str(outputs_dict[key]))

                    # Then add any remaining keys (excluding BaseURL, Model, and ECSServiceConnect)
                    for key, value in outputs_dict.items():
                        if (key not in priority_keys and
                            key != "BaseURL" and
                            key != "Model" and
                            "ECSServiceConnect" not in key and
                            value):  # Check if value is not empty and key doesn't contain ECSServiceConnect
                            models_table.add_row(key, str(value))
                elif outputs != '{}':  # Only show if not empty JSON
                    models_table.add_row("Outputs", outputs)
            elif outputs and outputs != '{}':  # Only show if not empty
                models_table.add_row("Outputs", outputs)
        except (SyntaxError, ValueError):
            # If parsing fails, only show the raw outputs if not empty
            if model_data.get('outputs') and model_data['outputs'] != '{}':
                models_table.add_row("Outputs", model_data['outputs'])

        # Add a real table line to split models
        if model_data != data[-1]:  # Don't add after the last model
            models_table.add_section()

    # Display the table
    console.print(models_table)

    # Display the Base URL section after the Models
    console.print("\nBase URL", style="bold")
    if base_url:
        console.print(base_url + "/v1")
        console.print("\nThe API uses an OpenAI-compatible format. Once you have the base URL and API key, you can access the API use the OpenAI SDK or any OpenAI-compatible client.")
        console.print(
            "[dim]Examples: [link=https://aws-samples.github.io/easy-model-deployer/en/openai_compatiable]https://aws-samples.github.io/easy-model-deployer/en/openai_compatiable[/link][/dim]\n",
        )
    else:
        console.print("No Base URL found")


if __name__ == "__main__":
    status()
