import os
import boto3
import typer
import packaging.version
from typing import Optional, Tuple
from rich.console import Console
from rich.panel import Panel

from emd.revision import VERSION
from emd.constants import ENV_STACK_NAME, ENV_BUCKET_NAME_PREFIX
from emd.utils.logger_utils import get_logger

logger = get_logger(__name__)


def get_deployed_infrastructure_version(region: str) -> Optional[str]:
    """Get the version of currently deployed infrastructure"""
    try:
        cfn = boto3.client('cloudformation', region_name=region)
        stack_info = cfn.describe_stacks(StackName=ENV_STACK_NAME)['Stacks'][0]

        # Get ArtifactVersion parameter from stack
        for param in stack_info.get('Parameters', []):
            if param['ParameterKey'] == 'ArtifactVersion':
                return param['ParameterValue']
    except Exception as e:
        logger.debug(f"Failed to get deployed infrastructure version: {e}")
    return None


def check_infrastructure_completeness(region: str) -> Tuple[bool, str]:
    """
    Check if EMD infrastructure is completely set up
    Returns: (is_complete, status_message)
    """
    try:
        cfn = boto3.client('cloudformation', region_name=region)
        s3 = boto3.client('s3', region_name=region)

        # Check CloudFormation stack
        try:
            stack_info = cfn.describe_stacks(StackName=ENV_STACK_NAME)['Stacks'][0]
            stack_status = stack_info['StackStatus']

            if stack_status not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
                return False, f"CloudFormation stack status: {stack_status}"

        except cfn.exceptions.ClientError as e:
            if "does not exist" in str(e):
                return False, "CloudFormation stack does not exist"
            raise

        # Check S3 bucket (get bucket name from stack resources)
        try:
            from emd.sdk.bootstrap import get_bucket_name
            bucket_name = get_bucket_name(
                bucket_prefix=ENV_BUCKET_NAME_PREFIX,
                region=region
            )
            s3.head_bucket(Bucket=bucket_name)
        except Exception as e:
            return False, f"S3 bucket issue: {str(e)}"

        return True, "Infrastructure is complete"

    except Exception as e:
        logger.debug(f"Infrastructure completeness check failed: {e}")
        return False, f"Infrastructure check failed: {str(e)}"


class SmartBootstrapManager:
    def __init__(self):
        self.console = Console()

    def check_version_compatibility(self, current_version: str, deployed_version: str, region: str) -> str:
        """
        Check version compatibility and infrastructure completeness
        Returns: 'auto_bootstrap', 'version_mismatch_warning', 'compatible'
        """
        if current_version == "0.0.0":
            logger.debug(f"Development build found")
            return 'auto_bootstrap'

        # First check if infrastructure is complete
        is_complete, status_msg = check_infrastructure_completeness(region)
        if not is_complete:
            logger.debug(f"Infrastructure incomplete: {status_msg}")
            return 'auto_bootstrap'  # Infrastructure missing/incomplete, need bootstrap

        if not deployed_version:
            return 'auto_bootstrap'  # No version info, need bootstrap

        try:
            current_parsed = packaging.version.parse(current_version)
            deployed_parsed = packaging.version.parse(deployed_version)

            if current_parsed > deployed_parsed:
                return 'auto_bootstrap'  # Local newer, auto bootstrap
            elif deployed_parsed > current_parsed:
                return 'version_mismatch_warning'  # Cloud newer, show warning
            else:
                return 'compatible'  # Same version, compatible
        except Exception as e:
            logger.debug(f"Failed to parse versions: {e}")
            return 'auto_bootstrap'  # Default to bootstrap if parsing fails

    def show_bootstrap_notification(self, current_version: str, deployed_version: str):
        """Show notification about automatic bootstrap"""
        self.console.print()  # Empty line for spacing
        if deployed_version:
            self.console.print(f"🔄 [bold green]Updating infrastructure...[/bold green] [dim]{deployed_version}[/dim] → [bold green]{current_version}[/bold green]")
        else:
            self.console.print(f"🚀 [bold green]Setting up infrastructure...[/bold green] [bold green]{current_version}[/bold green]")
        self.console.print()  # Empty line for spacing

    def show_version_mismatch_warning(self, current_version: str, deployed_version: str):
        """Show warning when cloud version is newer than local version"""
        self.console.print()  # Empty line for spacing
        self.console.print(f"⚠️  [bold yellow]Version mismatch:[/bold yellow] Local [dim]{current_version}[/dim] < Cloud [bold yellow]{deployed_version}[/bold yellow]")
        self.console.print(f"   [bold]Recommendation:[/bold] pip install --upgrade easy-model-deployer")
        self.console.print()  # Empty line for spacing


    def auto_bootstrap_if_needed(self, region: str) -> bool:
        """
        Automatically run bootstrap if needed based on comprehensive infrastructure check
        Returns: True if bootstrap was run, False otherwise
        """
        current_version = VERSION
        deployed_version = get_deployed_infrastructure_version(region)

        action = self.check_version_compatibility(current_version, deployed_version, region)

        if action == 'compatible':
            return False  # No action needed

        elif action == 'version_mismatch_warning':
            # Cloud version > Local version - show warning
            self.show_version_mismatch_warning(current_version, deployed_version)
            raise typer.Exit(0)

            return False  # User chose to continue, no bootstrap

        elif action == 'auto_bootstrap':
            # Infrastructure missing/incomplete OR version mismatch - ask for confirmation
            self.show_bootstrap_notification(current_version, deployed_version)

            # Ask for user confirmation
            if deployed_version:
                # Update scenario
                confirm_msg = f"Update infrastructure from {deployed_version} to {current_version}?"
            else:
                # Initialize scenario
                confirm_msg = f"Initialize EMD infrastructure for version {current_version}?"

            if not typer.confirm(confirm_msg, default=False):
                self.console.print("[yellow]Bootstrap cancelled. Infrastructure will not be updated.[/yellow]")
                self.console.print("[red]Deployment cannot proceed without compatible infrastructure.[/red]")
                raise typer.Exit(1)

            # User confirmed - proceed with bootstrap
            try:
                from emd.sdk.bootstrap import create_env_stack, get_bucket_name

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

                self.console.print("[bold green]✅ Infrastructure setup completed successfully![/bold green]")
                return True

            except Exception as e:
                self.console.print(f"[bold red]❌ Infrastructure setup failed: {str(e)}[/bold red]")
                raise typer.Exit(1)

        return False


# Global instance
smart_bootstrap_manager = SmartBootstrapManager()
