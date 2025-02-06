#!/usr/bin/env bash

set -euxo pipefail

# Build inference image and push it to private ECR repository
dockerfile='Dockerfile.inference.build.comfy.from_scratch'
repo_name='video-generation-comfy-ecr'
region='us-east-1'
tag='latest'
docker build  -t comfy-ecr -f Dockerfile.inference.build.comfy.from_scratch .
#aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/aws-gcr-solutions
#docker tag comfy-ecr:latest public.ecr.aws/aws-gcr-solutions/stable-diffusion-aws-extension/sivg-comfy-ecr:latest
#docker push public.ecr.aws/aws-gcr-solutions/stable-diffusion-aws-extension/sivg-comfy-ecr:latest