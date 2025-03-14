cd src/pipeline
# export model_id=DeepSeek-R1-Distill-Qwen-32B-GGUF
export model_id=Qwen2.5-72B-Instruct-AWQ
# export model_id=DeepSeek-R1-Distill-Qwen-32B
export model_tag=latest
python pipeline.py \
    --model_id ${model_id} \
    --model_tag latest \
    --model_s3_bucket "emd-test" \
    --backend_type tgi \
    --service_type local \
    --instance_type g5.12xlarge \
    --region us-west-2 \
    --framework_type fastapi \
    --role_name SageMakerExecutionRoleTest6 \
    --disable_parallel_prepare_and_build_image
