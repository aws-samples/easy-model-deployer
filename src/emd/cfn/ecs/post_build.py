import boto3
import time
import json
import os
import argparse
import sys
from emd.models.utils.serialize_utils import load_extra_params

# Post build script for ECS, it will deploy the VPC and ECS cluster.
CFN_ROOT_PATH = "../cfn"
WAIT_SECONDS = 10


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
                print(f"No updates are to be performed for stack {stack_name}.")

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


def deploy_vpc_template(region):
    client = boto3.client("cloudformation", region_name=region)
    stack_name = "EMD-VPC"
    template_path = f"{CFN_ROOT_PATH}/vpc/template.yaml"
    create_or_update_stack(client, stack_name, template_path)
    outputs = get_stack_outputs(client, stack_name)
    vpc_id = None
    subnets = None
    for output in outputs:
        if output["OutputKey"] == "VPCID":
            vpc_id = output["OutputValue"]
        elif output["OutputKey"] == "Subnets":
            subnets = output["OutputValue"]
    update_parameters_file("parameters.json", {"VPCID": vpc_id, "Subnets": subnets})
    return vpc_id, subnets


def deploy_ecs_cluster_template(region, vpc_id, subnets):
    client = boto3.client("cloudformation", region_name=region)
    stack_name = "EMD-ECS-Cluster"
    template_path = f"{CFN_ROOT_PATH}/ecs/cluster.yaml"
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
        ],
    )

    outputs = get_stack_outputs(client, stack_name)
    for output in outputs:
        update_parameters_file(
            "parameters.json", {output["OutputKey"]: output["OutputValue"]}
        )


def post_build():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", type=str, required=False)
    parser.add_argument("--model_id", type=str, required=False)
    parser.add_argument("--model_tag", type=str, required=False)
    parser.add_argument("--framework_type", type=str, required=False)
    parser.add_argument("--service_type", type=str, required=False)
    parser.add_argument("--backend_type", type=str, required=False)
    parser.add_argument("--model_s3_bucket", type=str, required=False)
    parser.add_argument("--instance_type", type=str, required=False)
    parser.add_argument(
        "--extra_params",
        type=load_extra_params,
        required=False,
        default=os.environ.get("extra_params", "{}"),
    )

    args = parser.parse_args()

    service_params = args.extra_params.get("service_params", {})

    if "vpc_id" not in service_params:
        vpc_id, subnets = deploy_vpc_template(args.region)
    else:
        vpc_id = service_params.get("vpc_id")
        subnets = service_params.get("subnet_ids")
        update_parameters_file("parameters.json", {"VPCID": vpc_id, "Subnets": subnets})

    deploy_ecs_cluster_template(args.region, vpc_id, subnets)


if __name__ == "__main__":
    post_build()
