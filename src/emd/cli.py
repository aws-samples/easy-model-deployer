import typer
from rich.console import Console
from rich.panel import Panel
from typing import Optional
from pathlib import Path
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import time
import os
from enum import Enum
import shutil
import zipfile
from emd.revision import VERSION, COMMIT_HASH

from emd.commands import (
    bootstrap,
    deploy,
    # models,
    destroy,
    version,
    status,
    config
)
from emd.commands.invoke import invoke
from emd.utils.aws_service_management import check_aws_environment
from typing_extensions import Annotated
from emd.utils.decorators import load_aws_profile,catch_aws_credential_errors
from emd.models import Model
import json

app = typer.Typer(
    add_completion=False,
    pretty_exceptions_enable=False
)
console = Console()

# Register commands from other modules
app.add_typer(
    bootstrap.app,
    name="bootstrap",
    help="Set up AWS environment for model deployment",
)
app.add_typer(
    deploy.app,
    name="deploy",
    help="Deploy a model",
)
app.add_typer(
    status.app,
    name="status",
    help="Query model status",
)

# app.add_typer(
#     deploy_status.app,
#     name="deploy-status",
#     help="query deploy status",
# )

app.add_typer(
    destroy.app,
    name="destroy",
    help="Destroy a model deployment",
)

app.add_typer(
    invoke.app,
    name="invoke",
    help="Invoke a model for testing, after deployment",
)

app.add_typer(
    config.app,
    name="config",
    help="Set default config",
)

app.add_typer(
    version.app,
    name="version",
    help="Show version",
)

@app.command(help="List supported models")
@catch_aws_credential_errors
def list_supported_models(model_id: Annotated[
        str, typer.Argument(help="Model ID")
    ] = None):
    # console.print("[bold blue]Retrieving models...[/bold blue]")
    support_models = Model.get_supported_models()
    if model_id:
        support_models = [model for _model_id,model in support_models.items() if _model_id == model_id]
    r = json.dumps(support_models,indent=2,ensure_ascii=False)
    print(f"{r}")

# app.add_typer(models.app, name="model",help="list supported models")

@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        # Show welcome message
        console.print(
            Panel.fit(
                f"[bold blue]Easy Model Deployer[/bold blue]\n[dim]Version: {VERSION}[/dim]\n[dim]Build  : {COMMIT_HASH}[/dim]",
                border_style="green",
            )
        )
        # Show main help
        console.print(ctx.get_help())
        console.print(
            " [dim]Further help: [link=https://github.com/aws-samples/easy-model-deployer]https://github.com/aws-samples/easy-model-deployer[/link][/dim]\n",
        )

if __name__ == "__main__":
    bootstrap.bootstrap()
