import boto3
import time
import json
import os
import argparse

# Post build script for ECS, it will deploy the VPC and ECS cluster.

CFN_ROOT_PATH = 'cfn'
WAIT_SECONDS = 10
# CFN_ROOT_PATH = '../../cfn'
JSON_DOUBLE_QUOTE_REPLACE = '<!>'

def load_extra_params(string):
    string = string.replace(JSON_DOUBLE_QUOTE_REPLACE,'"')
    try:
        return json.loads(string)
    except json.JSONDecodeError:
        raise argparse.ArgumentTypeError(f"Invalid dictionary format: {string}")

def dump_extra_params(d:dict):
    return json.dumps(d).replace('"', JSON_DOUBLE_QUOTE_REPLACE)

def wait_for_stack_completion(client, stack_id, stack_name):
    while True:
        stack_status = client.describe_stacks(StackName=stack_id)['Stacks'][0]['StackStatus']
        if stack_status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
            print(f"Stack {stack_name} deployment complete")
            break
        elif stack_status in ['CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS']:
            print(f"Stack {stack_name} is still being deployed...")
            time.sleep(WAIT_SECONDS)
        else:
            raise Exception(f"Stack {stack_name} deployment failed with status {stack_status}")

def get_stack_outputs(client, stack_name):
    response = client.describe_stacks(StackName=stack_name)
    return response['Stacks'][0].get('Outputs', [])

def create_or_update_stack(client, stack_name, template_path, parameters=[]):
    try:
        response = client.describe_stacks(StackName=stack_name)
        stack_status = response['Stacks'][0]['StackStatus']
        if stack_status in ['ROLLBACK_COMPLETE', 'ROLLBACK_FAILED', 'DELETE_FAILED']:
            print(f"Stack {stack_name} is in {stack_status} state. Deleting the stack to allow for recreation.")
            client.delete_stack(StackName=stack_name)
            while True:
                try:
                    response = client.describe_stacks(StackName=stack_name)
                    stack_status = response['Stacks'][0]['StackStatus']
                    if stack_status == 'DELETE_IN_PROGRESS':
                        print(f"Stack {stack_name} is being deleted...")
                        time.sleep(WAIT_SECONDS)
                    else:
                        raise Exception(f"Unexpected status {stack_status} while waiting for stack deletion.")
                except client.exceptions.ClientError as e:
                    if 'does not exist' in str(e):
                        print(f"Stack {stack_name} successfully deleted.")
                        break
                    else:
                        raise
        while stack_status not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
            if stack_status in ['CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS']:
                print(f"Stack {stack_name} is currently {stack_status}. Waiting for it to complete...")
                time.sleep(WAIT_SECONDS)
                response = client.describe_stacks(StackName=stack_name)
                stack_status = response['Stacks'][0]['StackStatus']
            else:
                raise Exception(f"Stack {stack_name} is in an unexpected state: {stack_status}")
        print(f"Stack {stack_name} already exists with status {stack_status}")
    except client.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            print(f"Stack {stack_name} does not exist. Proceeding with creation.")
            with open(template_path, 'r') as template_file:
                template_body = template_file.read()

            response = client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Parameters=parameters
            )

            stack_id = response['StackId']
            print(f"Started deployment of stack {stack_name} with ID {stack_id}")
            wait_for_stack_completion(client, stack_id, stack_name)
        else:
            raise

def update_parameters_file(parameters_path, updates):
    with open(parameters_path, 'r') as file:
        data = json.load(file)

    data['Parameters'].update(updates)

    with open(parameters_path, 'w') as file:
        json.dump(data, file, indent=4)

def deploy_vpc_template(region):
    client = boto3.client('cloudformation', region_name=region)
    stack_name = 'DMAA-VPC'
    template_path = f'{CFN_ROOT_PATH}/vpc/template.yaml'
    create_or_update_stack(client, stack_name, template_path)
    outputs = get_stack_outputs(client, stack_name)
    vpc_id = None
    subnets = None
    for output in outputs:
        if output['OutputKey'] == 'VPCID':
            vpc_id = output['OutputValue']
        elif output['OutputKey'] == 'Subnets':
            subnets = output['OutputValue']
    update_parameters_file('parameters.json', {'VPCID': vpc_id, 'Subnets': subnets})
    return vpc_id, subnets


def deploy_ecs_cluster_template(region, vpc_id, subnets):
    client = boto3.client('cloudformation', region_name=region)
    stack_name = 'DMAA-ECS-Cluster'
    template_path = f'{CFN_ROOT_PATH}/ecs/cluster.yaml'
    create_or_update_stack(client, stack_name, template_path, [
        {
            'ParameterKey': 'VPCID',
            'ParameterValue': vpc_id,
        },
        {
            'ParameterKey': 'Subnets',
            'ParameterValue': subnets,
        },
    ])

    outputs = get_stack_outputs(client, stack_name)
    for output in outputs:
        update_parameters_file('parameters.json', {output['OutputKey']: output['OutputValue']})


def post_build():
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', type=str, required=False)
    parser.add_argument('--model_id', type=str, required=False)
    parser.add_argument('--model_tag', type=str, required=False)
    parser.add_argument('--framework_type', type=str, required=False)
    parser.add_argument('--service_type', type=str, required=False)
    parser.add_argument('--backend_type', type=str, required=False)
    parser.add_argument('--model_s3_bucket', type=str, required=False)
    parser.add_argument('--instance_type', type=str, required=False)
    parser.add_argument('--extra_params', type=load_extra_params, required=False, default=os.environ.get("extra_params","{}"))

    args = parser.parse_args()

    service_params = args.extra_params.get('service_params',{})

    if 'vpc_id' not in service_params:
        vpc_id, subnets = deploy_vpc_template(args.region)
    else:
        vpc_id = service_params.get('vpc_id')
        subnets = service_params.get('subnet_ids')
        update_parameters_file('parameters.json', {'VPCID': vpc_id, 'Subnets': subnets})

    deploy_ecs_cluster_template(args.region, vpc_id, subnets)

if __name__ == "__main__":
    post_build()
