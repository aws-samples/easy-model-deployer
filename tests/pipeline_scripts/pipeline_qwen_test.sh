cd src/pipeline
python pipeline.py \
    --model_id Qwen2.5-7B-Instruct \
    --model_s3_bucket "llm-bot-dev-uiconstructuis3bucket14677a01-mjsoiqblq7wm" \
    --backend_type vllm \
    --service_type sagemaker \
    --instance_type g5.4xlarge \
    --region us-west-2 \
    --is_async_deploy false \
    --framework_type fastapi \
    --role_name SageMakerExecutionRoleTest6 \
    --vllm_cli_args "--max_num_seqs 20 --max_model_len 16000 --disable-log-stats"







