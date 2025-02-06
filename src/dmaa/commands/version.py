from dmaa.revision import VERSION
import typer
from dmaa.utils.decorators import load_aws_profile, catch_aws_credential_errors, check_dmaa_env_exist
from dmaa.utils.logger_utils import make_layout

app = typer.Typer()
layout = make_layout()


#@app.callback(invoke_without_command=True)(invoke_without_command=True)
@app.callback(invoke_without_command=True)
@catch_aws_credential_errors
@check_dmaa_env_exist
@load_aws_profile
def version():
    print(VERSION)
