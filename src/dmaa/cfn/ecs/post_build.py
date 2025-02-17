import boto3
import time
import json
import argparse

# Post build script for ECS, it will deploy the VPC and ECS cluster.

CFN_ROOT_PATH = 'cfn'
WAIT_SECONDS = 10
CFN_ROOT_PATH = '../../cfn'

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
        # if stack_status == 'ROLLBACK_COMPLETE':
        #     print(f"Stack {stack_name} is in ROLLBACK_COMPLETE state. Deleting the stack to allow for recreation.")
        #     client.delete_stack(StackName=stack_name)
        #     wait_for_stack_completion(client, stack_name, stack_name)
        while stack_status not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
            if stack_status in ['CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS']:
                print(f"Stack {stack_name} is currently {stack_status}. Waiting for it to complete...")
                time.sleep(SLEEP_WAIT_SECONDS)
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
    parser = argparse.ArgumentParser(description="Post build script")
    parser.add_argument('--region', type=str, required=False, help='AWS region')
    parser.add_argument('--model_id', type=str, required=False, help='Model ID')
    parser.add_argument('--model_tag', type=str, required=False, help='Model tag')
    parser.add_argument('--framework_type', type=str, required=False, help='Framework type')
    parser.add_argument('--service_type', type=str, required=False, help='Service type')
    parser.add_argument('--backend_type', type=str, required=False, help='Backend type')
    parser.add_argument('--model_s3_bucket', type=str, required=False, help='Model S3 bucket')
    parser.add_argument('--instance_type', type=str, required=False, help='Instance type')
    parser.add_argument('--extra_params', type=str, required=False, help='Extra parameters')

    args = parser.parse_args()

    extra_params = json.loads(args.extra_params) if args.extra_params else {}

    if 'vpc_id' not in extra_params:
        vpc_id, subnets = deploy_vpc_template(args.region)
    else:
        vpc_id = extra_params.get('vpc_id')
        subnets = extra_params.get('subnet_ids')
        update_parameters_file('parameters.json', {'VpcID': vpc_id, 'Subnets': subnets})

    deploy_ecs_cluster_template(args.region, vpc_id, subnets)

if __name__ == "__main__":
    post_build()
