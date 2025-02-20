#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

export PYTHONPATH=.:..:$PYTHONPATH
# pip install -r requirements.txt || { echo "Failed to install requirements"; exit 1; }

# region=cn-north-1
region=us-east-1
# region=us-west-2
export AWS_REGION=$region
model_s3_bucket=emd-us-east-1-bucket-75c6f785084f4fd998da560a0a6190fc
# model_s3_bucket=emd-cn-north-1-bucket-7cc5276c18f341bda8a457160936d78e
# model_id=Qwen2.5-7B-Instruct
model_id=Qwen2.5-0.5B-Instruct

# model_id=bge-base-en-v1.5

# model_id=Qwen/Qwen2.5-72B-Instruct-AWQ
backend_type=vllm
service=sagemaker
# service=ec2
gpu_num=1
instance_type=g5.12xlarge

# python deploy/prepare_model.py --region $region --model_id $model_id --model_s3_bucket $model_s3_bucket || { echo "Failed to prepare model"; exit 1; }
# python deploy/build_and_push_image.py --region $region --model_id $model_id --backend_type $backend_type --gpu_num $gpu_num --instance_type $instance_type --model_s3_bucket $model_s3_bucket --vllm_cli_args "--max_model_len 4096" || { echo "Failed to build and push image"; exit 1; }
# python deploy/deploy.py --region $region --instance_type $instance_type --model_id $model_id --backend_type $backend_type --service $service --gpu_num $gpu_num || { echo "Failed to deploy"; exit 1; }

python pipeline.py \
    --model_id $model_id \
    --model_s3_bucket $model_s3_bucket \
    --backend_type vllm \
    --service_type $service \
    --instance_type g5.4xlarge \
    --region $region \
    --is_async_deploy false \
    --framework_type fastapi \
    --role_name SageMakerExecutionRoleTest6 \
    --skip_image_build \
    --skip_deploy \
    --vllm_cli_args "--max_num_seqs 20 --max_model_len 16000 --disable-log-stats"

echo "Pipeline executed successfully"
