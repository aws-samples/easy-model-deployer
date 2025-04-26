# Build script for ECS Cluster, it will deploy a new VPC(optional) and ECS cluster.

import time
import json
import sys
import boto3
import subprocess

CFN_ROOT_PATH = "../cfn"
WAIT_SECONDS = 10

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {cmd}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def build_router_image(region):
    repo_name = "emd-openai-api-router"
    image_tag = f"{repo_name}:latest"

    # Check if repo exists
    try:
        run_command(f"aws ecr describe-repositories --repository-names {repo_name} --region {region}")
        print(f"ECR repository {repo_name} already exists")
    except:
        print(f"Creating ECR repository: {repo_name}")
        run_command(f"aws ecr create-repository --repository-name {repo_name} --region {region}")

    # Get ECR login
    account_id = json.loads(run_command(f"aws sts get-caller-identity --region {region}"))['Account']
    domain = f"dkr.ecr.{region}.amazonaws.com.cn" if region.startswith("cn-") else f"dkr.ecr.{region}.amazonaws.com"
    registry = f"{account_id}.{domain}"
    run_command(f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {registry}")
    # Build image
    print(f"Building Docker image with tag: {image_tag}")
    build_cmd = (
        f"cd {CFN_ROOT_PATH}/shared/openai_router && docker build " +
        ("--build-arg GOPROXY=https://goproxy.cn,direct " if region.startswith("cn-") else "") +
        f"-t {image_tag} ."
    )
    run_command(build_cmd)

    # Tag and push image
    full_image_tag = f"{registry}/{image_tag}"

    print(f"Tagging image as: {full_image_tag}")
    run_command(f"docker tag {image_tag} {full_image_tag}")

    print(f"Pushing image to ECR: {full_image_tag}")
    run_command(f"docker push {full_image_tag}")

    return full_image_tag

def wait_for_stack_completion(client, stack_name):
    while True:
        response = client.describe_stacks(StackName=stack_name)
        stack_status = response["Stacks"][0]["StackStatus"]
        while stack_status.endswith("IN_PROGRESS"):
            print(
                f"Stack {stack_name} is currently {stack_status}. Waiting for completion..."
            )
            time.sleep(WAIT_SECONDS)
            response = client.describe_stacks(StackName=stack_name)
            stack_status = response["Stacks"][0]["StackStatus"]

        if stack_status in ["CREATE_COMPLETE", "UPDATE_COMPLETE"]:
            print(f"Stack {stack_name} deployment complete")
            break
        else:
            print(
                f"Post build stage failed. The stack {stack_name} is in an unexpected status: {stack_status}. Please visit the AWS CloudFormation Console to delete the stack."
            )
            sys.exit(1)

def get_stack_outputs(client, stack_name):
    response = client.describe_stacks(StackName=stack_name)
    return response["Stacks"][0].get("Outputs", [])


def create_or_update_stack(client, stack_name, template_path, parameters=[]):
    try:
        wait_for_stack_completion(client, stack_name)
        response = client.describe_stacks(StackName=stack_name)
        stack_status = response["Stacks"][0]["StackStatus"]

        if stack_status in ["CREATE_COMPLETE", "UPDATE_COMPLETE"]:
            print(f"Stack {stack_name} already exists. Proceeding with update.")
            with open(template_path, "r") as template_file:
                template_body = template_file.read()
            try:
                response = client.update_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Capabilities=["CAPABILITY_NAMED_IAM"],
                    Parameters=parameters
                )
            except Exception as e:
                print(f"No updates are to be performed for stack {stack_name}. " + str(e))

            print(f"Started update of stack {stack_name}")
            wait_for_stack_completion(client, stack_name)

    except client.exceptions.ClientError as e:
        if "does not exist" in str(e):
            print(f"Stack {stack_name} does not exist. Proceeding with creation.")
            with open(template_path, "r") as template_file:
                template_body = template_file.read()

            response = client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=["CAPABILITY_NAMED_IAM"],
                Parameters=parameters,
                EnableTerminationProtection=True,
            )

            stack_id = response["StackId"]
            print(f"Started deployment of stack {stack_name} with ID {stack_id}")
            wait_for_stack_completion(client, stack_name)
        else:
            print(
                f"Post build stage failed. The stack {stack_name} is in an unexpected status: {stack_status}. Please visit the AWS CloudFormation Console to delete the stack."
            )
            sys.exit(1)


def update_parameters_file(parameters_path, updates):
    with open(parameters_path, "r") as file:
        data = json.load(file)

    data["Parameters"].update(updates)

    with open(parameters_path, "w") as file:
        json.dump(data, file, indent=4)


def remove_parameters_file(parameter_path, parameters):
    with open(parameter_path, "r") as file:
        data = json.load(file)

    for param in parameters:
        if param in data["Parameters"]:
            del data["Parameters"][param]

    with open(parameter_path, "w") as file:
        json.dump(data, file, indent=4)


def deploy_vpc_template(region):
    client = boto3.client("cloudformation", region_name=region)
    stack_name = "EMD-VPC"
    template_path = f"{CFN_ROOT_PATH}/shared/vpc.yaml"
    create_or_update_stack(client, stack_name, template_path)
    outputs = get_stack_outputs(client, stack_name)
    vpc_id = None
    subnets = None
    for output in outputs:
        if output["OutputKey"] == "VPCID" and output["OutputValue"]:
            vpc_id = output["OutputValue"]
        elif output["OutputKey"] == "Subnets" and output["OutputValue"]:
            subnets = output["OutputValue"]

    update_parameters_file("parameters.json", {"VPCID": vpc_id, "Subnets": subnets})
    return vpc_id, subnets


def deploy_ecs_cluster_template(region, vpc_id, subnets, use_spot):
    client = boto3.client("cloudformation", region_name=region)
    stack_name = "EMD-ECS-Cluster"
    template_path = f"{CFN_ROOT_PATH}/shared/ecs_cluster.yaml"
    create_or_update_stack(
        client,
        stack_name,
        template_path,
        [
            {
                "ParameterKey": "VPCID",
                "ParameterValue": vpc_id,
            },
            {
                "ParameterKey": "Subnets",
                "ParameterValue": subnets,
            },
            {
                "ParameterKey": "UseSpot",
                "ParameterValue": "yes" if use_spot else "no",
            },
        ],
    )

    outputs = get_stack_outputs(client, stack_name)
    for output in outputs:
        update_parameters_file(
            "parameters.json", {output["OutputKey"]: output["OutputValue"]}
        )


def deploy_ecs_cluster(region, vpc_id=None, subnets=None, use_spot=False):
    """Deploy ECS cluster with specified VPC and subnets.

    Args:
        region (str): AWS region to deploy to
        vpc_id (str, optional): VPC ID to use for deployment. If None, deploys new VPC.
        subnets (str, optional): Comma-separated list of subnet IDs. If None, deploys new VPC.
    """

    # Deploy new VPC if no vpc_id/subnets provided
    if not vpc_id or not subnets:
        vpc_id, subnets = deploy_vpc_template(region)

    # Update parameters with networking info
    update_parameters_file("parameters.json", {"VPCID": vpc_id, "Subnets": subnets})

    # Build and push Fargate image to ECR as the OpenAI compatible API router
    # api_router_uri = build_router_image(region)

    # Deploy the ECS cluster
    deploy_ecs_cluster_template(region, vpc_id, subnets, use_spot)

if __name__ == "__main__":
    deploy_ecs_cluster("us-east-1")
