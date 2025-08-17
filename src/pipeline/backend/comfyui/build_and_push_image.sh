#!/bin/bash

# Initialize default values
region="us-east-1"
tag="latest"
image_name="vllm-on-sagemaker"

# Parse named arguments
while [ "$#" -gt 0 ]; do
  case "$1" in
    --region) region="$2"; shift 2;;
    --tag) tag="$2"; shift 2;;
    --image-name) image_name="$2"; shift 2;;
    --) shift; break;;
    *) echo "Unknown option: $1" >&2; exit 1;;
  esac
done

# Get the account number associated with the current IAM credentials
account=$(aws sts get-caller-identity --query Account --output text)
if [ "$?" -ne 0 ]; then
    exit 255
fi

echo "Building docker image: $image_name"
echo "region: $region"
echo "account: $account"
echo "tag: $tag"

function build_and_push_image() {
    local account="$1"
    local region="$2"
    local image_name="$3"
    local docker_file="$4"
    local policy_file="$5"

    if [[ $region == *cn* ]]; then
       image_fullname="${account}.dkr.ecr.${region}.amazonaws.com.cn/${image_name}:${tag}"
       ecr_repo_uri="${account}.dkr.ecr.${region}.amazonaws.com.cn"
    else
       image_fullname="${account}.dkr.ecr.${region}.amazonaws.com/${image_name}:${tag}"
       ecr_repo_uri="${account}.dkr.ecr.${region}.amazonaws.com"
    fi

    # If the repository doesn't exist in ECR, create it
    aws ecr describe-repositories --repository-names "${image_name}" --region "${region}" > /dev/null 2>&1 || aws ecr create-repository --repository-name "${image_name}" --region "${region}"

    # Get the login command from ECR and execute it directly
    aws ecr get-login-password --region "${region}" | \
	docker login --username AWS --password-stdin "${ecr_repo_uri}"

    # Update ECR policy file with current account ID
    sed -i "s/{{ACCOUNT_ID}}/${account}/g" "${policy_file}"

    aws ecr set-repository-policy \
        --repository-name "${image_name}" \
        --policy-text "file://${policy_file}" \
        --region "${region}"

    # Build the docker image locally with the image name and then push it to ECR
    # with the full name.
    build_context="${script_dir/..}"
    docker build --platform linux/amd64 -t "${image_name}" -f ${docker_file} .
    docker tag "${image_name}" "${image_fullname}"
    docker push "${image_fullname}"
}

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo $script_dir

docker_file="$script_dir/Dockerfile"
policy_file="$script_dir/ecr-policy.json"

build_and_push_image "${account}" "${region}" "${image_name}" "${docker_file}" "${policy_file}" "${script_dir}"
