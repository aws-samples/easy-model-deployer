import boto3
import time
import json
import os
import argparse
import sys
from emd.models.utils.serialize_utils import load_extra_params
from emd.cfn.shared.ecs_cluster import deploy_ecs_cluster, remove_parameters_file
# Post build script for SageMaker OpenAI Compatible Interface, it will deploy the VPC and ECS cluster with an API router Fargate ECS service.


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

    if "vpc_id" in service_params:
        vpc_id = service_params.get("vpc_id")
        subnets = service_params.get("subnet_ids")
    else:
        vpc_id = None
        subnets = None

    if "use_spot" in service_params and service_params.get("use_spot") == "true":
        use_spot = True
    else:
        use_spot = False

    deploy_ecs_cluster(args.region, vpc_id, subnets, use_spot)


if __name__ == "__main__":
    post_build()
