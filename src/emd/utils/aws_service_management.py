import boto3
import typer
import time
import os
from botocore.exceptions import ClientError, NoCredentialsError
from emd.constants import ENV_STACK_NAME
from emd.utils.aws_service_utils import get_current_region

from rich.console import Console

console = Console()

def log_status_message(status, title, icon):
    status_colors = {
        "InProgress": "yellow",
        "Failed": "red",
        "Succeeded": "green",
        "Pending": "white"
    }
    current_time = time.strftime("%H:%M:%S", time.localtime())
    color = status_colors.get(status, "white")
    title = title.ljust(28)
    console.print(f"{icon}", f"[{current_time}]", f"[{color}]{title}: {status}[/{color}]")

def check_aws_environment():
    """
    Check if AWS environment is properly configured by attempting to access AWS services.
    Raises typer.Exit if AWS is not configured correctly.
    """
    try:
        # Try to create a boto3 client and make a simple API call
        sts = boto3.client('sts', region_name=get_current_region())
        response = sts.get_caller_identity()
        typer.echo("AWS environment is properly configured.")
        account_id = response['Account']
        region = boto3.session.Session().region_name
        typer.echo(f"AWS Account: {account_id}")
        typer.echo(f"AWS Region: {region}")
    except (ClientError, NoCredentialsError):
        typer.echo("Error: AWS credentials not found or invalid.")
        typer.echo("Please configure your AWS credentials using:")
        typer.echo("  aws configure")
        raise typer.Exit(1)

def log_pipeline_execution_details(execution_id: str = None, logs: bool = False):
    """
    Get the details of a pipeline execution and optionally log the events.
    """
    try:
        sts = boto3.client("sts", region_name=get_current_region())
        region = get_current_region()
        cfn = boto3.client("cloudformation", region_name=region)
        codepipeline = boto3.client("codepipeline", region_name=region)
        with console.status("[bold blue]Retrieving model deployment status... (Press Ctrl+C to return)[/bold blue]"):
            # Check if CloudFormation stack exists for CodePipeline
            bootstrap_stack = cfn.describe_stacks(
                StackName=ENV_STACK_NAME
            )["Stacks"][0]
            # Get the pipeline name from the bootstrap stack
            pipeline_resources = [
                resource
                for resource in cfn.describe_stack_resources(
                    StackName=bootstrap_stack["StackName"]
                )["StackResources"]
                if resource["ResourceType"] == "AWS::CodePipeline::Pipeline"
            ]
            pipeline_name = pipeline_resources[0]["PhysicalResourceId"]
            if not execution_id:
                # Get the last pipeline execution
                pipeline_executions = codepipeline.list_pipeline_executions(pipelineName=pipeline_name, maxResults=1)
                if not pipeline_executions["pipelineExecutionSummaries"]:
                    console.print("[red]No pipeline executions found.[/red]")
                    return

                last_execution = pipeline_executions["pipelineExecutionSummaries"][0]
                execution_id = last_execution["pipelineExecutionId"]
                execution_status = last_execution["status"]
            else:
                execution_status = codepipeline.get_pipeline_execution(
                    pipelineName=pipeline_name,
                    pipelineExecutionId=execution_id,
                )["pipelineExecution"]["status"]

            build_log = []
            if execution_status == "InProgress":
                while execution_status == "InProgress":
                    time.sleep(4)
                    execution = codepipeline.get_pipeline_execution(
                        pipelineName=pipeline_name,
                        pipelineExecutionId=execution_id,
                    )
                    execution_status = execution["pipelineExecution"]["status"]
                    pipeline_state = codepipeline.get_pipeline_state(name=pipeline_name)
                    source_stage = pipeline_state["stageStates"][0]["latestExecution"] if "latestExecution" in pipeline_state["stageStates"][0] else {}
                    build_stage = pipeline_state["stageStates"][1]["latestExecution"] if "latestExecution" in pipeline_state["stageStates"][1] else {}
                    deploy_stage = pipeline_state["stageStates"][2]["latestExecution"] if "latestExecution" in pipeline_state["stageStates"][2] else {}
                    try:
                        if build_stage["status"] == "InProgress":
                            build_execution_id = pipeline_state["stageStates"][1]["actionStates"][0]["latestExecution"]["externalExecutionId"]
                        codebuild = boto3.client("codebuild", region_name=region)
                        build_logs = codebuild.batch_get_builds(ids=[build_execution_id])
                        # Retrieve the latest log and print
                        if build_logs["builds"]:
                            latest_build = build_logs["builds"][0]
                            log_group_name = latest_build["logs"]["groupName"]
                            log_stream_name = latest_build["logs"]["streamName"]
                            logs_client = boto3.client("logs", region_name=region)
                            log_events = logs_client.get_log_events(
                                logGroupName=log_group_name,
                                logStreamName=log_stream_name,
                                startFromHead=False
                            )
                            if log_events["events"]:
                                last_events = log_events["events"][-10:]
                                for event in last_events:
                                    if event['message'].strip():
                                        build_log.append(event['message'].strip())
                    except KeyError:
                        pass

                    console.clear()
                    for log in build_log:
                        console.print(f"  {log}", no_wrap=True, crop=True)
                    try:
                        if execution_id == source_stage["pipelineExecutionId"]:
                            log_status_message(source_stage["status"], "Model files preparation", ":factory:")
                        else:
                            log_status_message("Pending", "Model files preparation", ":factory:")
                        if execution_id == build_stage["pipelineExecutionId"]:
                            log_status_message(build_stage["status"], "Model image building", ":truck:")
                        else:
                            log_status_message("Pending", "Model image building", ":truck:")
                        if execution_id == deploy_stage["pipelineExecutionId"]:
                            log_status_message(deploy_stage["status"], "Model service deployment", ":ship:")
                        else:
                            log_status_message("Pending", "Model service deployment", ":ship:")
                    except Exception as e:
                        pass
            # Retrieve pipeline execution details
            execution_details = codepipeline.get_pipeline_execution(
                pipelineName=pipeline_name,
                pipelineExecutionId=execution_id,
            )

            # Retrieve the variables from the pipeline execution
            variables = execution_details["pipelineExecution"].get("variables", [])
            model_id = None
            for variable in variables:
                if variable["name"] == "ModelId":
                    model_id = variable["resolvedValue"]
                    break

            console.print(f"Model deployment task is stopped. Last status: [bold red]{execution_status}[/bold red]")
            console.print(f"Model ID: [bold red]{model_id}[/bold red]")
            if execution_status == "Succeeded":
                pipeline_state = codepipeline.get_pipeline_state(name=pipeline_name)
                last_stage = pipeline_state["stageStates"][-1]
                last_stage_name = last_stage["stageName"]
                # Extract the CloudFormation stack ID from the externalExecutionId
                if "actionStates" in last_stage:
                    for action in last_stage["actionStates"]:
                        if "latestExecution" in action:
                            external_execution_id = action["latestExecution"].get("externalExecutionId")
                if external_execution_id and "stackId=" in external_execution_id:
                    stack_name = external_execution_id.split("stack/")[-1].split("/")[0]
                    # Get the CloudFormation stack by ARN
                    try:
                        stack_details = cfn.describe_stacks(StackName=stack_name)["Stacks"][0]
                        # Get the stack output list
                        stack_outputs = stack_details.get("Outputs", [])
                        if stack_outputs:
                            for output in stack_outputs:
                                console.print(f"{output['OutputKey']}: [bold red]{output['OutputValue']}[/bold red]")
                    except ClientError as e:
                        return
            elif execution_status == "Failed":
                # Retrieve the failed stage details
                pipeline_state = codepipeline.get_pipeline_state(name=pipeline_name)
                failed_stage = next((stage for stage in pipeline_state["stageStates"] if stage.get("latestExecution",{}).get("status") == "Failed"), None)
                if failed_stage:
                    failed_stage_name = failed_stage["stageName"]
                    failed_stage_action = failed_stage["actionStates"][0]
                    failed_stage_execution_id = failed_stage_action["latestExecution"]["externalExecutionId"]
                    console.print(f"Deployment failed at: [bold red]{failed_stage_name}[/bold red]")
                    # Retrieve the reason for the failure
                    if "errorDetails" in failed_stage_action["latestExecution"]:
                        error_details = failed_stage_action["latestExecution"]["errorDetails"]
                        error_code = error_details.get("code", "Unknown")
                        error_message = error_details.get("message", "No error message provided.")
                        console.print(f"Error Message: [red]{error_message}[/red]")
                else:
                    console.print("[red]Pipeline execution failed, but the failed stage could not be determined.[/red]")
    except (ClientError, NoCredentialsError) as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[red]Error: AWS credentials not found or invalid.[/red]")
        console.print("Please configure your AWS credentials using:")
        console.print("  aws configure")
        raise typer.Exit(1)
