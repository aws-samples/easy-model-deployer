import typer
from rich.console import Console
from rich.panel import Panel

from dmaa.constants import MODEL_DEFAULT_TAG, VERSION_MODIFY
from typing_extensions import Annotated
from dmaa.sdk.destroy import destroy as sdk_destroy
from dmaa.utils.decorators import catch_aws_credential_errors,check_dmaa_env_exist,load_aws_profile
from dmaa.utils.logger_utils import make_layout
from dmaa.revision import convert_version_name_to_stack_name

app = typer.Typer()
console = Console()
layout = make_layout()


#@app.callback(invoke_without_command=True)(invoke_without_command=True)
@app.callback(invoke_without_command=True)
@catch_aws_credential_errors
@check_dmaa_env_exist
@load_aws_profile
def destroy(
    model_id: Annotated[
        str, typer.Argument(help="Model ID"),
    ],
    model_tag: Annotated[
        str, typer.Argument(help="Model tag")
    ] = MODEL_DEFAULT_TAG,
    model_deploy_version: Annotated[
        str, typer.Option("-v", "--deploy-version", help="The version of the model deployment to destroy"),
    ] = VERSION_MODIFY
    ):
    model_deploy_version = convert_version_name_to_stack_name(model_deploy_version)
    # console.print("[bold blue]Checking AWS environment...[/bold blue]")
    sdk_destroy(model_id,model_tag=model_tag,waiting_until_complete=True, model_deploy_version=model_deploy_version)
