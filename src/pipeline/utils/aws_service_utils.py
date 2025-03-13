import boto3
import time
import os
from botocore.exceptions import ClientError, NoCredentialsError
from .logger_utils import get_logger
import json
import hashlib
import boto3
logger = get_logger(__name__)


def calculate_md5_string(input_string):
    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode('utf-8'))
    return md5_hash.hexdigest()


def check_aws_environment():
    """
    Check if AWS environment is properly configured by attempting to access AWS services.
    Raises typer.Exit if AWS is not configured correctly.
    """
    try:
        # Try to create a boto3 client and make a simple API call
        sts = boto3.client('sts')
        response = sts.get_caller_identity()
        logger.info("AWS environment is properly configured.")
        account_id = response['Account']
        region = boto3.session.Session().region_name
        logger.info(f"AWS Account: {account_id}\nAWS Region: {region}")
    except (ClientError, NoCredentialsError):
        logger.info("Error: AWS credentials not found or invalid.\nPlease configure your AWS credentials using:\naws configure")


def get_account_id():
    sts_client = boto3.client("sts", region_name=get_current_region())
    account_id = sts_client.get_caller_identity()["Account"]
    return account_id

def create_s3_bucket(bucket_name,region):
    s3 = boto3.client('s3')
    try:
        s3.head_bucket(Bucket=bucket_name)
    except:
        try:
            if region == 'us-east-1':
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            # Enable versioning on the bucket
            s3.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
        except (s3.exceptions.BucketAlreadyOwnedByYou,):
            logger.info(f"bucket: {bucket_name} exists")
        except Exception as e:
            raise


def get_role_create_template(
        role_name:str,
        services_to_assume:list[str],
        manage_policy_arns:list[str]
    ):
    role_create_template = {
      "Type": "AWS::IAM::Role",
      "Properties": {
        "RoleName": role_name,
        "AssumeRolePolicyDocument": {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "Service": service
              },
              "Action": "sts:AssumeRole"
            }
            for service in services_to_assume
          ]
        },
        "ManagedPolicyArns": manage_policy_arns
      }
    }
    return role_create_template


def get_stack_info(stack_name):
    cf = boto3.client('cloudformation', region_name=get_current_region())
    stack_info = cf.describe_stacks(StackName=stack_name)['Stacks'][0]
    return stack_info



# def check_cn_region(region:str):
#     return region.startswith("cn")
