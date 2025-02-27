from emd.revision import VERSION, COMMIT_HASH
import typer
from emd.utils.logger_utils import make_layout

app = typer.Typer(pretty_exceptions_enable=False)
layout = make_layout()


#@app.callback(invoke_without_command=True)(invoke_without_command=True)
@app.callback(invoke_without_command=True)
def version():
    print(f"emd {VERSION} (build {COMMIT_HASH})")
