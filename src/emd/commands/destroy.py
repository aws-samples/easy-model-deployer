import typer
from rich.console import Console
from rich.panel import Panel

from emd.constants import MODEL_DEFAULT_TAG
from typing_extensions import Annotated
from emd.sdk.destroy import destroy as sdk_destroy
from emd.utils.decorators import catch_aws_credential_errors,check_emd_env_exist,load_aws_profile
from emd.utils.logger_utils import make_layout
from emd.revision import convert_version_name_to_stack_name

app = typer.Typer(pretty_exceptions_enable=False)
console = Console()
layout = make_layout()


#@app.callback(invoke_without_command=True)(invoke_without_command=True)
@app.callback(invoke_without_command=True)
@catch_aws_credential_errors
@check_emd_env_exist
@load_aws_profile
def destroy(
    model_id: Annotated[
        str, typer.Argument(help="Model ID"),
    ],
    model_tag: Annotated[
        str, typer.Argument(help="Model tag")
    ] = MODEL_DEFAULT_TAG
    ):
    # console.print("[bold blue]Checking AWS environment...[/bold blue]")
    sdk_destroy(model_id,model_tag=model_tag,waiting_until_complete=True)
