cd src/pipeline
python pipeline.py \
    --model_id whisper \
    --backend_type huggingface \
    --service_type sagemaker_realtime \
    --instance_type g5.2xlarge \
    --region us-west-2 \
    --is_async_deploy false \
    --framework_type fastapi \
