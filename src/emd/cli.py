import typer
from emd.commands import (
    bootstrap,
    deploy,
    models,
    destroy,
    version,
    status,
    config
)
from emd.commands.invoke import invoke
from emd.revision import VERSION, COMMIT_HASH
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    add_completion=False,
    pretty_exceptions_enable=False
)
console = Console()

# Register commands from other modules
app.add_typer(
    bootstrap.app,
    name="bootstrap",
    help="Initialize AWS resources for model deployment",
)
app.add_typer(
    deploy.app,
    name="deploy",
    help="Deploy models to AWS infrastructure",
)
app.add_typer(
    status.app,
    name="status",
    help="Display status of deployed models",
)

# app.add_typer(
#     deploy_status.app,
#     name="deploy-status",
#     help="query deploy status",
# )

app.add_typer(
    invoke.app,
    name="invoke",
    help="Test deployed models with sample requests",
)

app.add_typer(
    destroy.app,
    name="destroy",
    help="Remove deployed models and clean up resources",
)

app.add_typer(models.app, name="list-supported-models", help="Display available models")

app.add_typer(
    config.app,
    name="profile",
    help="Configure AWS profile credentials",
)

app.add_typer(
    version.app,
    name="version",
    help="Display tool version information",
)

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
