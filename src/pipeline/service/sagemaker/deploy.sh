model_id=$1
backend=$2

export REGION='us-east-1' # change as needed
export IMG_NAME="emd-${backend}" # change as needed
export IMG_TAG='latest' # change as needed
export SAGEMAKER_ENDPOINT_NAME="emd-${backend}-on-sagemaker-2"
export INSTANCE_TYPE='g5.2xlarge' # change as needed
export IMG_NAME="emd-${backend}" # change as needed
echo "#!/bin/bash
export BACKEND=${backend}
export MODEL_ID=${model_id}
python3 src/deploy/on_sagemaker/sagemaker_serving.py" > src/deploy/on_sagemaker/serve

bash src/backend/$backend/build_and_push_image.sh --region "$REGION" --image-name "$IMG_NAME" --tag "$IMG_TAG"

export IMG_URI=$(bash src/deploy/get_ecr_image_uri.sh --region "$REGION" --img-name "$IMG_NAME" --tag "$IMG_TAG")
echo $IMG_URI

# export SM_ROLE=$(bash src/deploy/on_sagemaker/create_sagemaker_execute_role.sh)
SM_ROLE='arn:aws:iam::544919262599:role/SageMakerExecutionRoleTest'
echo $SM_ROLE

echo $MODEL_ID
python3 src/deploy/on_sagemaker/create_sagemaker_endpoint.py \
    --region "$REGION" \
    --model_id "$MODEL_ID" \
    --instance_type $INSTANCE_TYPE \
    --role_arn $SM_ROLE \
    --image_uri $IMG_URI \
    --endpoint_name $SAGEMAKER_ENDPOINT_NAME
