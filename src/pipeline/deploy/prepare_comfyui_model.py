import time
import os
import subprocess
import logging
import uuid
import argparse

import boto3
from huggingface_hub import snapshot_download
from emd.models import Model

from utils.common import upload_dir_to_s3_by_s5cmd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--region", type=str, default=os.environ.get("region","us-east-1"))
parser.add_argument(
    "--model_id",
    type=str,
    default=os.environ.get("model_id",None),
    help="Currently supports txt2video_LTX",
)
parser.add_argument("--model_s3_bucket", type=str, default=os.environ.get('model_s3_bucket',"emd-us-east-1-bucket-1234567890"))
args = parser.parse_known_args()[0]

# User defined variables
region = args.region
model_id = args.model_id
model_s3_bucket = args.model_s3_bucket

model = Model.get_model(model_id)
huggingface_model_list = model.huggingface_model_list
huggingface_url_list = model.huggingface_url_list

# Prepare model
os.environ["AWS_REGION"] = region
model_dir = f"emd_models/{model_id}"
# Create S3 bucket
# logger.info(f"Creating S3 bucket {model_s3_bucket}")
# boto3.client("s3", region_name=region).create_bucket(Bucket=model_s3_bucket, CreateBucketConfiguration={"LocationConstraint": region})
# Download model
os.makedirs(model_dir, exist_ok=True)
if huggingface_model_list is not None:
    for key, value in huggingface_model_list.items():
        logger.info(f"Downloading {key} model")
        huggingface_model_id = key
        model_local_dir = os.path.join(model_dir, value)
        os.makedirs(model_local_dir, exist_ok=True)
        snapshot_download(repo_id=huggingface_model_id, local_dir=model_local_dir)

if huggingface_url_list is not None:
    for key, value in huggingface_url_list.items():
        logger.info(f"Downloading {os.path.basename(key)} model")
        huggingface_model_url = key
        model_local_dir = os.path.join(model_dir, value)
        os.makedirs(model_local_dir, exist_ok=True)
        subprocess.run(["wget", "-P", model_local_dir, huggingface_model_url])
# Upload model to S3
logger.info(f"Uploading comfyui models to S3")
upload_dir_to_s3_by_s5cmd(model_s3_bucket, model_dir)
