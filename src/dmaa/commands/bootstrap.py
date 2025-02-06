import typer
from rich.console import Console
from typing import Optional
from dmaa.constants import ENV_STACK_NAME,ENV_BUCKET_NAME_PREFIX
from typing_extensions import Annotated
from dmaa.sdk.bootstrap import create_env_stack,get_bucket_name
from dmaa.utils.decorators import catch_aws_credential_errors, load_aws_profile
from dmaa.utils.logger_utils import make_layout
from dmaa.utils.aws_service_utils import get_current_region

app = typer.Typer()
console = Console()
layout = make_layout()

@app.callback(invoke_without_command=True)
@catch_aws_credential_errors
@load_aws_profile
def bootstrap(
    skip_confirm: Annotated[
        Optional[bool], typer.Option("--skip-confirm", help="Skip confirmation")
    ] = False,
):

    region = get_current_region()
    typer.echo("AWS environment is properly configured.")
    layout["main"].update("[bold red]Initalizing environment...[/bold red]")
    try:
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
        console.print(f"[bold green]Successfully bootstrapped DMAA environment[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error deploying CloudFormation stack: {str(e)}[/bold red]")
        raise typer.Exit(1)