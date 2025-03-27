import os
import logging
import argparse
import boto3
from emd.utils.aws_service_utils import get_current_region

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

instance_to_gpus = {
    "g5.4xlarge": 1,    # A10G （24 GB）
    "g6.4xlarge": 1,    # L4 （24 GB）
    "g5.12xlarge": 4,   # A10G （24 GB * 4）
    "g6.12xlarge": 4,   # L4（24 GB * 4）
    "g5.48xlarge": 8,   # A10G（24 GB * 8）
    "g6.48xlarge": 8,   # L4 （24 GB * 4）
    "p4d.24xlarge": 8,  # A100 （40 GB * 8）
    "p4de.24xlarge": 8, # A100 （80 GB * 8）
    "p5.48xlarge": 8,   # H100 （80 GB * 8）
}

def get_num_gpus(instance_type):
    try:
        return instance_to_gpus[instance_type]
    except KeyError:
        raise ValueError(f"Instance type {instance_type} not found in the dictionary")

def download_dir_from_s3(bucket_name, remote_dir_name):
    logger.info(f"Downloading {remote_dir_name} from {bucket_name} bucket")
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=remote_dir_name):
        if not os.path.exists(os.path.dirname(obj.key)):
            os.makedirs(os.path.dirname(obj.key))
        bucket.download_file(obj.key, obj.key)

def download_dir_from_s3_by_s5cmd(local_dir,bucket_name=None, s3_key=None,model_files_s3_path=None):
    if model_files_s3_path is None:
        assert bucket_name and s3_key,(bucket_name,s3_key)
        model_files_s3_path = f"s3://{bucket_name}/{s3_key}"

    logger.info(f"Downloading model files from {model_files_s3_path}")
    assert os.system(f"./s5cmd cp {model_files_s3_path}/* {local_dir}") == 0

def download_file_from_s3_by_s5cmd(s3_file_path, local_file_path):
    """
    Download a file from S3 using s5cmd.

    Args:
        s3_file_path (str): The S3 file path (e.g., s3://bucket/key).
        local_file_path (str): The local file path to save the downloaded file.
    """
    logger.info(f"Downloading {s3_file_path} to {local_file_path}")
    os.system(f"./s5cmd cp {s3_file_path} {local_file_path}")

def upload_dir_to_s3(bucket_name, local_dir_name):
    logger.info(f"Uploading {local_dir_name} to {bucket_name} bucket")
    s3 = boto3.client('s3', region_name=get_current_region())
    for root, dirs, files in os.walk(local_dir_name):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_dir_name)
            s3_path = os.path.join(local_dir_name, relative_path)
            s3.upload_file(local_path, bucket_name, s3_path)

def upload_dir_to_s3_by_s5cmd(bucket_name, local_dir_name):
    logger.info(f"Uploading {local_dir_name} to {bucket_name} bucket")
    if len(local_dir_name.split("/")) > 1:
        s3_key = "/".join(local_dir_name.split("/")[:-1])
        s3_path = f"s3://{bucket_name}/{s3_key}/"
    else:
        s3_path = f"s3://{bucket_name}/"
    assert os.system(f"./s5cmd cp {local_dir_name} {s3_path}") == 0


def sync_s3_files_or_folders_to_local(s3_bucket, s3_key, local_path):
    logger.info("sync_s3_models_or_inputs_to_local start")
    s5cmd_command = f'./s5cmd sync s3://{s3_bucket}/{s3_key}/* {local_path}/'
    try:
        logger.info(s5cmd_command)
        os.system(s5cmd_command)
        logger.info(f'Files copied from "s3://{s3_bucket}/{s3_key}" to "{local_path}/"')
        return True
    except Exception as e:
        logger.info(f"Error executing s5cmd command: {e}")
        return False

def sync_local_outputs_to_s3(s3_bucket, s3_key, local_path):
    logger.info("sync_local_outputs_to_s3 start")
    s5cmd_command = f'./s5cmd sync "{local_path}/*" "s3://{s3_bucket}/comfy/{s3_key}/" '
    try:
        logger.info(s5cmd_command)
        os.system(s5cmd_command)
        logger.info(f'Upload results "{local_path}/" to "s3://{s3_bucket}/comfy/{s3_key}/"')
        clean_cmd = f'rm -rf {local_path}'
        os.system(clean_cmd)
        logger.info(f'Files removed from local {local_path}')
    except Exception as e:
        logger.info(f"Error executing s5cmd command: {e}")


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
