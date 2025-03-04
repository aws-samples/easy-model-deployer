import typer
from rich.console import Console
import boto3
from typing import Annotated
from emd.utils.decorators import catch_aws_credential_errors

from emd.patch_questionary.select_with_help import select_with_help,Choice
from emd.utils.profile_manager import profile_manager
from emd.utils.cli_styles import custom_style

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False
)
console = Console()


@app.command(help="Set the default profile name for deployment")
@catch_aws_credential_errors
def set_default_profile_name(
    name: Annotated[
        str,
        typer.Argument(help="profile name")
    ]=None
):
    session = boto3.Session()
    profiles = session.available_profiles
    if name is not None:
        assert name in profiles, f"Profile {name} not found in available profiles {profiles}"
    else:
        if profiles:
            # if len(profiles) > 1:
            choices = []
            for profile_name in profiles:
                session = boto3.Session(profile_name=profile_name)
                region = session.region_name
                choices.append(
                    Choice(
                        title=profile_name,
                        description=f"ProfileName: {profile_name}, Region: {region}"
                    )
                )

            # choices.insert(0,Choice(title=EMD_USE_NO_PROFILE_CHOICE, description="Manually enter the AK/SK"))
            name = select_with_help(
                "Select the profile for deployment:",
                choices=choices,
                style=custom_style
            ).ask()

    if not name:
        console.print(f"[bold blue]No profile set[/bold blue]")
        return
    profile_manager.write_default_profile_name_to_local(name)
    console.print(f"set default profile: {name} to {profile_manager.profile_path}")


@app.command(help="Show current default profile")
@catch_aws_credential_errors
def show_default_profile_name():
    name = profile_manager.load_profile_name_from_local()
    if name:
        console.print(f"[bold blue]Current profile: {name}[/bold blue]")
    else:
        console.print(f"[bold blue]No default profile to show[/bold blue]")


@app.command(help="Remove the default profile")
@catch_aws_credential_errors
def remove_default_profile_name():
    name = profile_manager.remove_profile_name_from_local()
    if name:
        console.print(f"[bold blue]Default profile: {name} removed[/bold blue]")
    else:
        console.print(f"[bold blue]No default profile to remove[/bold blue]")
