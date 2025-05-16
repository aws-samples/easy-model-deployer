import typer
from rich.console import Console
from rich.panel import Panel
from typing import Optional
# from pathlib import Path
import boto3
# from botocore.exceptions import ClientError, NoCredentialsError
# import time
import os
import json
import re
from collections import defaultdict

from emd.constants import MODEL_TAG_PATTERN,MODEL_DEFAULT_TAG,LOCAL_REGION
from emd.utils.aws_service_utils import get_current_region
from typing_extensions import Annotated
from emd.models import Model
from emd.models.services import Service
from emd.models.instances import Instance
from emd.models.utils.constants import InstanceType,EngineType,ServiceType
# from emd.utils.text_utilities import random_suffix, normalize, enum_to_choices, enum_to_strings
from emd.patch_questionary.select_with_help import select_with_help,Choice
from emd.sdk.deploy import deploy as sdk_deploy,deploy_local as sdk_deploy_local
from emd.sdk.deploy import parse_extra_params
from emd.utils.aws_service_utils import check_cn_region
import questionary
from emd.utils.accelerator_utils import get_gpu_num,check_cuda_exists,check_neuron_exists
from emd.utils.decorators import catch_aws_credential_errors,check_emd_env_exist,load_aws_profile
from emd.utils.logger_utils import make_layout
from emd.utils.exceptions import ModelNotSupported,ServiceNotSupported,InstanceNotSupported
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter

app = typer.Typer(pretty_exceptions_enable=False)
console = Console()
layout = make_layout()

# model_instance_choices = enum_to_strings(ModelInstance)

from questionary import Style

custom_style = Style([
    ('qmark', 'fg:#66BB6A bold'),
    ('question', 'fg:default'),
    ('answer', 'fg:#4CAF50 bold'),
    ('pointer', 'fg:#66BB6A bold'),
    ('highlighted', 'fg:#4CAF50 bold'),
    ('selected', 'fg:#A5D6A7 bold'),
    ('disabled', 'fg:#CED4DA italic'),
    ('error', 'fg:#F44336 bold'),
])

def show_help(choice):
    return f"{choice} (shortcut)"


def supported_models_filter(
    region:str,
    allow_local_deploy,
    only_allow_local_deploy,
    support_models:list[Model]
):
    ret = []
    is_cn_region = check_cn_region(region)

    for model in support_models:
        if is_cn_region and not model.allow_china_region:
            continue

        # Skip models that only support local services when local deployment is not allowed
        if not allow_local_deploy:
            # Check if all supported services are local services
            all_local_services = all(service.service_type == ServiceType.LOCAL for service in model.supported_services)
            if all_local_services:
                continue

        ret.append(model)
    return ret

def supported_services_filter(
        region,
        allow_local_deploy,
        only_allow_local_deploy,
        supported_services:list[Service]):
    ret = []
    is_cn_region = check_cn_region(region)
    for service in supported_services:
        if is_cn_region and not service.support_cn_region:
            continue
        if service.service_type == ServiceType.LOCAL and not allow_local_deploy:
            continue
        ret.append(service)

    if only_allow_local_deploy:
        ret = [service for service in ret if service.service_type == ServiceType.LOCAL]
    if not ret:
        raise ServiceNotSupported(region)
    return ret

def supported_instances_filter(
        region,
        allow_local_deploy:bool,
        only_allow_local_deploy:bool,
        supported_instances:list[Instance]):
    ret = []
    is_cn_region = check_cn_region(region)
    for instance in supported_instances:
        if is_cn_region and not instance.support_cn_region:
            continue

        if instance.instance_type == InstanceType.LOCAL and not allow_local_deploy:
            continue
        ret.append(instance)

    if only_allow_local_deploy:
        ret = [instance for instance in ret if instance.instance_type == InstanceType.LOCAL]
    if not ret:
        raise InstanceNotSupported(region)
    return ret



def check_model_support_on_cn_region(model_id,region):
    model = Model.get_model(model_id)
    is_cn_region = check_cn_region(region)
    if is_cn_region and not model.allow_china_region:
        return False
    return True

def check_service_support_on_cn_region(serivce_type, region):
    service = Service.get_service_from_service_type(serivce_type)
    is_cn_region = check_cn_region(region)
    if is_cn_region and not service.support_cn_region:
        return False
    return True

def check_instance_support_on_cn_region(instance_type, region):
    instance = Instance.get_instance_from_instance_type(instance_type)
    is_cn_region = check_cn_region(region)
    if is_cn_region and not instance.support_cn_region:
        return False
    return True

def is_valid_model_tag(name,pattern=MODEL_TAG_PATTERN):
    return bool(re.match(pattern, name))


def natural_sort_key(s):
    # Split the string into text and numeric parts
    return [int(c) if c.isdigit() else float(c) if c.replace('.', '', 1).isdigit() else c.lower()
            for c in re.split(r'(\d+\.\d+|\d+)', s)]


def ask_model_id(region, allow_local_deploy, only_allow_local_deploy, model_id=None):
    if model_id is not None:
        return model_id

    try:
        supported_models = [Model.get_model(m) for m in Model.get_supported_models()]
        filtered_models = supported_models_filter(region, allow_local_deploy, only_allow_local_deploy, supported_models)

        if not filtered_models:
            raise ModelNotSupported(region)

        model_ids = sorted([model.model_id for model in filtered_models], key=natural_sort_key)
        completer = FuzzyWordCompleter(model_ids, WORD=True)

        from prompt_toolkit.formatted_text import HTML
        from prompt_toolkit import PromptSession
        from prompt_toolkit.application.current import get_app

        session = PromptSession(
            completer=completer,
            complete_while_typing=True,
            rprompt=HTML('<span fg="#888888">(Run "emd list-supported-models" for full model list)</span>')
        )

        def get_prompt_message():
            return HTML('<b>? Enter model name: </b>')

        while True:
            selected_model = session.prompt(
                get_prompt_message,
                pre_run=lambda: get_app().current_buffer.start_completion()
            )

            if not selected_model:
                console.print("[bold yellow]Model selection cancelled[/bold yellow]")
                raise typer.Exit(0)

            if selected_model not in model_ids:
                console.print(f"[bold #FFA726]Invalid model name, please try again or press Ctrl+C to cancel[/bold #FFA726]")
                continue

            return selected_model

    except Exception as e:
        if not isinstance(e, (ModelNotSupported, typer.Exit)):
            console.print(f"[bold #FFA726]Error during model selection: {str(e)}[/bold #FFA726]")
            raise typer.Exit(1)
        raise


#@app.callback(invoke_without_command=True)(invoke_without_command=True)
@app.callback(invoke_without_command=True)
@catch_aws_credential_errors
@check_emd_env_exist
@load_aws_profile
def deploy(
    model_id: Annotated[str,typer.Option("--model-id",help="Model id")
    ] = None,
    instance_type: Annotated[
        str, typer.Option("-i", "--instance-type", help="The instance type to use")
    ] = None,
    engine_type: Annotated[
        str, typer.Option("-e", "--engine-type", help="The name of the inference engine")
    ] = None,
    service_type: Annotated[
        str, typer.Option("-s", "--service-type", help="The name of the service")
    ] = None,
    framework_type:Annotated[
        str, typer.Option("--framework-type", help="The name of the framework")
    ] = None,
    model_tag: Annotated[
        str, typer.Option("--model-tag", help="give a model tag,this is useful to create multiple models with same model id")
    ] = MODEL_DEFAULT_TAG,
    extra_params: Annotated[
        str, typer.Option("--extra-params",help="extra params (Json string)")
    ] = None,
    skip_confirm: Annotated[
        Optional[bool], typer.Option("--skip-confirm", help="Skip confirmation")
    ] = False,
    force_update_env_stack:Annotated[
        Optional[bool], typer.Option("--force-update-env-stack", help="force update env stack")
    ] = False,
    allow_local_deploy:Annotated[
        Optional[bool], typer.Option("--allow-local-deploy", help="allow local instance")
    ] = False,
    only_allow_local_deploy: Annotated[
        Optional[bool], typer.Option("--only-allow-local-deploy", help="only allow local instance")
    ] = False,
    dockerfile_local_path: Annotated[
        str, typer.Option("--dockerfile-local-path", help="Your custom Dockerfile path for building the model image, all files must be in the same directory")
    ] = None,
    local_gpus:Annotated[
        str, typer.Option("--local-gpus", help="Local gpu ids to deploy the model (e.g. `0,1,2`), only working with local deployment mode.")
    ] = None,
):
    if only_allow_local_deploy:
        allow_local_deploy = True
        region = LOCAL_REGION
    else:
        region = get_current_region()

    if dockerfile_local_path:
        response = sdk_deploy(
            model_id='custom-docker',
            model_tag=f"{model_id}-{model_tag}",
            instance_type=instance_type,
            engine_type='custom',
            framework_type='custom',
            service_type='sagemaker_realtime',
            region=region,
            extra_params = extra_params,
            env_stack_on_failure = "ROLLBACK",
            force_env_stack_update = force_update_env_stack,
            waiting_until_deploy_complete=True,
            dockerfile_local_path=dockerfile_local_path,
        )
        return response

    vpc_id = None
    # ask model id
    model_id = ask_model_id(
        region,
        allow_local_deploy,
        only_allow_local_deploy,
        model_id=model_id
    )

    if not check_model_support_on_cn_region(model_id,region):
        raise ModelNotSupported(region,model_id=model_id)


    model = Model.get_model(model_id)
    # support services
    supported_services:list[Service] = model.supported_services
    supported_services = supported_services_filter(
        region,
        allow_local_deploy,
        only_allow_local_deploy,
        supported_services
    )
    if service_type is None:
        if len(supported_services) > 1:
            service_name = select_with_help(
                "Select model hosting service:",
                choices=[
                    Choice(
                        title=service.name,
                        description=service.description
                    )
                    for service in supported_services
                ],
                style=custom_style
            ).ask()
            try:
                service_type = Service.get_service_from_name(service_name).service_type
            except:
                raise typer.Exit(0)
        else:
            service_type = supported_services[0].service_type
            console.print(f"[bold blue]service type: {supported_services[0].name}[/bold blue]")
    else:
        supported_service_types = model.supported_service_types
        console.print(f"[bold blue]service type: {service_type}[/bold blue]")
        assert service_type in supported_service_types, \
            f"Invalid service type: {service_type}, supported service types for model: {model_id}: {supported_service_types}"

    if service_type is None:
        raise typer.Exit(0)

    if not check_service_support_on_cn_region(service_type,region):
        raise ServiceNotSupported(region, service_type=service_type)

    if Service.get_service_from_service_type(service_type).need_vpc:
        client = boto3.client('ec2', region_name=region)
        vpcs = []
        emd_default_vpc = None
        paginator = client.get_paginator('describe_vpcs')
        for page in paginator.paginate():
            for vpc in page['Vpcs']:
                if any(tag['Key'] == 'Name' and tag['Value'] == 'EMD-vpc' for tag in vpc.get('Tags', [])):
                    emd_default_vpc = vpc
                    continue
                vpcs.append(vpc)
        else:
            for vpc in vpcs:
                vpc_name = next((tag['Value'] for tag in vpc.get('Tags', []) if tag.get('Key') == 'Name'), None)
                vpc['Name'] = vpc_name if vpc_name else '-'
            emd_vpc = select_with_help(
                "Select VPC (Virtual Private Cloud):",
                choices=[
                    Choice(
                        title=f"{emd_default_vpc['VpcId']} ({emd_default_vpc['CidrBlock']}) (EMD-vpc)" if emd_default_vpc else 'Create a new VPC',
                        description='Use the existing EMD-VPC for the new model deployment (recommended)' if emd_default_vpc else 'Create a new VPC with two public subnets and a S3 Endpoint for the model deployment. Select this option if you do not know what is VPC',
                    )
                ] + [
                    Choice(
                        title=f"{vpc['VpcId']} ({vpc['CidrBlock']}) ({vpc['Name']})",
                        description="Custom VPC requirement: A NAT Gateway or S3 Endpoint, with at least two public and two private subnet.",
                    )
                    for vpc in vpcs
                ],
                style=custom_style
            ).ask()

        vpc_id = None
        selected_subnet_ids = []
        if 'Create a new VPC' == emd_vpc:
            pass
        elif 'EMD-vpc' in emd_vpc:
            vpc_id = emd_vpc.split()[0]
            paginator = client.get_paginator('describe_subnets')
            for page in paginator.paginate(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]):
                for subnet in page['Subnets']:
                    selected_subnet_ids.append(subnet['SubnetId'])
        else:
            vpc_id = emd_vpc.split()[0]
            subnets = []
            paginator = client.get_paginator('describe_subnets')
            for page in paginator.paginate(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]):
                for subnet in page['Subnets']:
                    subnets.append(subnet)
            if not subnets:
                console.print("[bold red]No subnets found in the selected VPC.[/bold red]")
                raise typer.Exit(0)
            else:
                for subnet in subnets:
                    subnet_name = next((tag['Value'] for tag in subnet.get('Tags', []) if tag.get('Key') == 'Name'), None)
                    subnet['Name'] = subnet_name if subnet_name else '-'
                selected_subnet = questionary.checkbox(
                    "Select multiple subnets for the model deployment:",
                    choices=[
                        f"{subnet['SubnetId']} ({subnet['CidrBlock']}) ({subnet['Name']})"
                        for subnet in subnets
                    ],
                    style=custom_style
                ).ask()
                if selected_subnet is None:
                    raise typer.Exit(0)
                else:
                    for subnet in selected_subnet:
                        selected_subnet_ids.append(subnet.split()[0])

    # support instance
    supported_instances = model.supported_instances
    supported_instances = supported_instances_filter(
        region,
        allow_local_deploy,
        only_allow_local_deploy,
        supported_instances
    )
    if service_type == ServiceType.LOCAL:
        if check_cuda_exists():
            if local_gpus is not None:
                os.environ['CUDA_VISIBLE_DEVICES']=local_gpus
            elif os.environ.get('CUDA_VISIBLE_DEVICES'):
                pass
            else:
                gpu_num = get_gpu_num()
                support_gpu_num = model.supported_instances[0].gpu_num
                support_gpu_num = support_gpu_num or gpu_num
                default_gpus_str = ",".join([str(i) for i in range(min(gpu_num,support_gpu_num))])
                gpus_to_deploy = questionary.text(
                        "input the local gpu ids to deploy the model (e.g. 0,1,2):",
                        default=f"{default_gpus_str}"
                    ).ask()
                os.environ['CUDA_VISIBLE_DEVICES']=gpus_to_deploy
            console.print(f"[bold blue]local gpus: {os.environ.get('CUDA_VISIBLE_DEVICES')}[/bold blue]")
        instance_type = InstanceType.LOCAL
    else:
        if instance_type is None:
            if len(supported_instances)>1:
                instance_type = select_with_help(
                    "Select instance type:",
                    choices=[
                        Choice(
                            title=instance.instance_type,
                            description=(instance.description + '\n\n' +
                                "Note: If your deployment takes over 20 minutes, check your AWS service quotas, especially for G or P instances. Quotas are based on vCPUs, not instance count. Ensure your requests fit the limits. See Amazon EC2 instance type quotas for detail: https://docs.aws.amazon.com/ec2/latest/instances/ec2-instance-quota-types.html."
                            )
                        )
                        for instance in supported_instances
                    ],
                    style=custom_style
                ).ask()
            else:
                instance_type = supported_instances[0].instance_type
                console.print(f"[bold blue]instance type: {instance_type}[/bold blue]")

        else:
            supported_instance_types = model.supported_instance_types
            console.print(f"[bold blue]instance type: {instance_type}[/bold blue]")
            assert instance_type in supported_instance_types,\
                    f"Invalid instance type: {instance_type}, supoorted instance types for model: {model_id}: {supported_instance_types}"

    if instance_type is None:
        raise typer.Exit(0)

    if not check_instance_support_on_cn_region(instance_type,region):
        raise InstanceNotSupported(region, instance_type=instance_type)

    supported_engines = model.supported_engines
    if Instance.check_inf2_instance(instance_type):
        supported_engines = [engine for engine in supported_engines if engine.support_inf2_instance]
    # filter engines that unsupported on selected instance type
    # supported_engines = [engine for engine in supported_engines if instance_type in engine.supported_instance_types]

    if engine_type is None:
        if len(supported_engines)>1:
            engine_type = select_with_help(
                "Select inference engine:",
                choices=[
                    Choice(
                        title=engine.engine_type,
                        description=engine.description
                    )
                    for engine in supported_engines
                ],
                style=custom_style
            ).ask()
        else:
            engine_type = supported_engines[0].engine_type
            console.print(f"[bold blue]engine type: {engine_type}[/bold blue]")
    else:
        supported_engine_types = model.supported_engine_types
        console.print(f"[bold blue]engine type: {engine_type}[/bold blue]")
        assert engine_type in supported_engine_types,\
                f"Invalid engine type: {engine_type}, supported engine types for model: {model_id}: {supported_engine_types}"

    if engine_type is None:
        raise typer.Exit(0)

    # framework
    supported_frameworks = model.supported_frameworks
    if framework_type is None:
        if len(supported_frameworks)>1:
            framework_type = select_with_help(
                "Select inference engine:",
                choices=[
                    Choice(
                        title=framework.framework_type,
                        description=framework.description
                    )
                    for framework in supported_frameworks
                ],
                style=custom_style
            ).ask()
        else:
            framework_type = supported_frameworks[0].framework_type
    else:
        supported_framework_types = model.supported_framework_types
        console.print(f"[bold blue]framework type: {framework_type}[/bold blue]")
        assert framework_type in supported_framework_types,\
                f"Invalid engine type: {framework_type}, supported framwork types for model: {model_id}: {supported_framework_types}"

    if framework_type is None:
        raise typer.Exit(0)

    # extra_params
    if extra_params is None:
        while True:
            extra_params = questionary.text(
                "(Optional) Additional parameters, usage (https://aws-samples.github.io/easy-model-deployer/en/best_deployment_practices/#extra-parameters-usage), you can skip by pressing Enter:",
                default="{}"
            ).ask()

            try:
                extra_params = parse_extra_params(extra_params)
                break
            except json.JSONDecodeError as e:
                console.print("[red]Invalid JSON format. Please try again.[/red]")
    else:
        try:
            extra_params = parse_extra_params(extra_params)
        except json.JSONDecodeError as e:
            console.print("[red]Invalid JSON format. Please try again.[/red]")

    # append extra params for VPC and subnets
    if vpc_id:
        if 'service_params' not in extra_params:
            extra_params['service_params'] = {}
        extra_params['service_params']['vpc_id'] = vpc_id
        extra_params['service_params']['subnet_ids'] = ",".join(selected_subnet_ids)
    # model tag
    if not skip_confirm and not service_type == ServiceType.LOCAL:
        while True:
            model_tag = questionary.text(
                    "(Optional) Custom tag (label), you can skip by pressing Enter:",
                    default=MODEL_DEFAULT_TAG
                ).ask()
            # if model_tag == MODEL_DEFAULT_TAG:
            #     console.print(f"[bold blue]invalid model tag: {model_tag}. Please try again.[/bold blue]")
            # else:
            #     console.print(f"[bold blue] model tag: {model_tag}[/bold blue]")
            #     break
            try:
                if not model_tag and not is_valid_model_tag(model_tag):
                    console.print(f"[bold blue]invalid model tag: {model_tag}. Please ensure that the tag complies with the standard rules: {MODEL_TAG_PATTERN}.[/bold blue]")
                else:
                    break
            except:
                raise typer.Exit(0)

    if not model_tag:
        raise ValueError("Model tag is required.")
        # model_tag = MODEL_DEFAULT_TAG

    if not skip_confirm:
        if not typer.confirm(
            "Ready to deploy? Please confirm your selections above.",
            abort=True,
        ):
            raise typer.Exit(0)

    # log the deployment parameters
    engine_info = model.find_current_engine(engine_type)
    framework_info = model.find_current_framework(framework_type)

    engine_info_str = json.dumps(engine_info,indent=2,ensure_ascii=False)
    framework_info_str = json.dumps(framework_info, indent=2, ensure_ascii=False)
    extra_params_info = json.dumps(extra_params, indent=2, ensure_ascii=False)
    console.print(f"[bold blue]Deployment parameters:[/bold blue]")
    console.print(f"[bold blue]model_id: {model_id},model_tag: {model_tag}[/bold blue]")
    console.print(f"[bold blue]instance_type: {instance_type}[/bold blue]")
    console.print(f"[bold blue]service_type: {service_type}[/bold blue]")
    console.print(f"[bold blue]engine info:\n {engine_info_str}[/bold blue]")
    console.print(f"[bold blue]framework info:\n {framework_info_str}[/bold blue]")
    console.print(f"[bold blue]extra_params:\n {extra_params_info}[/bold blue]")
    # Start pipeline execution
    if service_type != ServiceType.LOCAL:
        response = sdk_deploy(
            model_id=model_id,
            instance_type=instance_type,
            engine_type=engine_type,
            service_type=service_type,
            region=region,
            extra_params = extra_params,
            model_tag=model_tag,
            env_stack_on_failure = "ROLLBACK",
            force_env_stack_update = force_update_env_stack,
            waiting_until_deploy_complete=True
        )
        console.print(f"[bold green]Model deployment pipeline execution initiated. Execution ID: {response['pipeline_execution_id']}[/bold green]")
    else:
        response = sdk_deploy_local(
            model_id=model_id,
            instance_type=instance_type,
            engine_type=engine_type,
            service_type=service_type,
            model_tag=MODEL_DEFAULT_TAG,
            # region=region,
            extra_params = extra_params
        )
    return response
