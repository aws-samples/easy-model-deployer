#!/bin/bash

# Set the region and determine the partition
REGION=$1  # Change as needed
if [[ $REGION == cn-* ]]; then
    PARTITION="aws-cn"
else
    PARTITION="aws"
fi

# Define the trust policy
TRUST_POLICY='{
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
}'

ROLE_NAME=SageMakerExecutionRoleTest

# Detach existing policies and delete the role if it exists
aws iam list-attached-role-policies --role-name $ROLE_NAME --query 'AttachedPolicies[*].PolicyArn' --output text | xargs -n 1 aws iam detach-role-policy --role-name $ROLE_NAME --policy-arn
aws iam delete-role --role-name $ROLE_NAME

# Create the role and capture the role ARN
SAGEMAKER_ROLE_ARN=$(aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document "$TRUST_POLICY" --query 'Role.Arn' --output text)

# Attach SageMaker full access policy
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:$PARTITION:iam::aws:policy/AmazonSageMakerFullAccess

# Attach S3 read-only access policy
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:$PARTITION:iam::aws:policy/AmazonS3ReadOnlyAccess

# Attach ECR read-only access policy
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:$PARTITION:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly

# Attach assume role policy
# aws iam attach-role-policy \
#     --role-name $ROLE_NAME \
#     --policy-arn arn:$PARTITION:iam::aws:policy/service-role/AmazonAssumeRolePolicy

echo "$SAGEMAKER_ROLE_ARN"