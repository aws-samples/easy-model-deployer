import boto3
import argparse
import json 
import time 
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_or_create_role(role_name, region):
    iam_client = boto3.client('iam')
    # to allow assuming role when visit sagemaker 
    trust_policy = json.dumps({
            "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "sagemaker.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
    try:
        role_arn = iam_client.get_role(RoleName=role_name)['Role']['Arn']
        iam_client.update_assume_role_policy(
            PolicyDocument=trust_policy,
            RoleName=role_name,
        )  
    except iam_client.exceptions.NoSuchEntityException:
        role = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=trust_policy
        )
        role_arn  = role['Role']['Arn']
    
    # attach policy
    if region.startswith("cn"):
        permission_policies = [
            "arn:aws-cn:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
            "arn:aws-cn:iam::aws:policy/AmazonS3FullAccess",
            "arn:aws-cn:iam::aws:policy/AmazonSageMakerFullAccess"
        ]
    else:
        permission_policies = [
            "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
            "arn:aws:iam::aws:policy/AmazonS3FullAccess",
            "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
        ]
    for policy in permission_policies:
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy
        )
    
    return role_arn


def create_sagemaker_endpoint(
        region, 
        instance_type,
        role_arn,
        image_uri,
        endpoint_name, 
        model_id,
        is_async_deploy=False,
        s3_output_path=None
    ):
    sagemaker = boto3.client('sagemaker', region_name=region)
    create_model_response = sagemaker.create_model(
        ModelName=endpoint_name + '-model',
        PrimaryContainer={
            'Image': image_uri,
            'Environment': {
                'API_HOST': '0.0.0.0',
                'API_PORT': '8080',
                'MODEL_ID': model_id,
                'INSTANCE_TYPE': instance_type,
            },
        },
        ExecutionRoleArn=role_arn,
    )
    
    endpoint_config_kwargs = dict(
        EndpointConfigName=endpoint_name + '-config',
        ProductionVariants=[
            {
                'VariantName': 'default',
                'ModelName': endpoint_name + '-model',
                'InstanceType': instance_type,
                'InitialInstanceCount': 1,
            },
        ]
    )
    if is_async_deploy:
        logger.info("Async deploy enabled")
        assert s3_output_path is not None,f"s3_output_path must be provided when is_async_deploy is True"
        async_inference_config={
            'OutputConfig': {
                'S3OutputPath': s3_output_path,
                # 'KmsKeyId': 'arn:aws:kms:region:account-id:key/key-id',  # 可选：KMS 密钥
            },
            # 'NotificationConfig': {
            #     'SuccessTopic': 'arn:aws:sns:region:account-id:my-success-topic',  # 可选：成功通知 SNS 主题
            #     'ErrorTopic': 'arn:aws:sns:region:account-id:my-error-topic',  # 可选：错误通知 SNS 主题
            # }
        }
        endpoint_config_kwargs['AsyncInferenceConfig'] = async_inference_config

    create_endpoint_config_response = sagemaker.create_endpoint_config(
        **endpoint_config_kwargs
    )

    create_endpoint_response = sagemaker.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=endpoint_name + '-config',
    )

    resp = sagemaker.describe_endpoint(EndpointName=endpoint_name)
    status = resp["EndpointStatus"]
    print("Status: " + status)
    print(f"Endpoint {endpoint_name} created. Check on the sagemaker console.")

    while status == "Creating":
        time.sleep(60)
        resp = sagemaker.describe_endpoint(EndpointName=endpoint_name)
        status = resp["EndpointStatus"]
        print("Status: " + status)

    print("Arn: " + resp["EndpointArn"])
    print("Status: " + status)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', default='us-east-1', help='The region to create the endpoint')
    parser.add_argument('--model_id', required=True, help='The Hugging Face model ID to use')
    parser.add_argument('--instance_type', required=True, help='Instance type for the SageMaker endpoint')
    parser.add_argument('--role_arn', required=True, help='The ARN of the IAM role for SageMaker to access resources')
    parser.add_argument('--image_uri', required=True, help='The URI of the Docker image in ECR')
    parser.add_argument('--endpoint_name', default='vllm-endpoint', help='The name of the endpoint to create')

    args = parser.parse_args()

    create_sagemaker_endpoint(
        region=args.region,
        instance_type=args.instance_type,
        role_arn=args.role_arn,
        image_uri=args.image_uri,
        endpoint_name=args.endpoint_name,
        model_id=args.model_id,
    )