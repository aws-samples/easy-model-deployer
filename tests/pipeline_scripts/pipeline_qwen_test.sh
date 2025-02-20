cd src/pipeline
export model_id=Qwen2.5-0.5B-Instruct
export model_tag=latest
python pipeline.py \
    --model_id Qwen2.5-0.5B-Instruct \
    --model_tag latest \
    --model_s3_bucket "emd-test" \
    --backend_type vllm \
    --service_type local \
    --instance_type g5.4xlarge \
    --region us-west-2 \
    --framework_type fastapi \
    --role_name SageMakerExecutionRoleTest6 \
    --disable_parallel_prepare_and_build_image
