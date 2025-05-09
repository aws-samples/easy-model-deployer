import json
from typing import Optional

import typer
from emd.models import Model
from emd.utils.decorators import catch_aws_credential_errors
from rich.console import Console
from typing_extensions import Annotated

app = typer.Typer(pretty_exceptions_enable=False)
console = Console()

@app.callback(invoke_without_command=True)
@catch_aws_credential_errors
def list_supported_models(
    model_id: Annotated[
        str, typer.Argument(help="Model ID")
    ] = None,
    detail: Annotated[
        Optional[bool],
        typer.Option("-a", "--detail", help="output model information in details.")
    ] = False
):
    # console.print("[bold blue]Retrieving models...[/bold blue]")
    support_models = Model.get_supported_models(detail=detail)
    if model_id:
        support_models = [model for _model_id,model in support_models.items() if _model_id == model_id]
    r = json.dumps(support_models,indent=2,ensure_ascii=False)
    print(f"{r}")
