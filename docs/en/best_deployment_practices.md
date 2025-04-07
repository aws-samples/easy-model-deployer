# Best Deployment Practices

This document provides examples of best practices for deploying models using EMD for various use cases.

## Famous Models

### Mistral Small Series
```
emd deploy --model-id Mistral-Small-3.1-24B-Instruct-2503 --instance-type g5.12xlarge --engine-type vllm --service-type sagemaker_realtime
```

### Gemma 3 Series

```
emd deploy --model-id gemma-3-27b-it --instance-type g5.12xlarge --engine-type vllm --service-type sagemaker_realtime
```

### Qwen Series

#### Qwen2.5-VL-32B-Instruct

```bash
emd deploy --model-id Qwen2.5-VL-32B-Instruct --instance-type g5.12xlarge --engine-type vllm --service-type sagemaker_realtime
```

#### QwQ-32B

```bash
emd deploy --model-id QwQ-32B --instance-type g5.12xlarge --engine-type vllm --service-type sagemaker_realtime
```

## Deploying to Specific GPU Types

Choosing the right GPU type is critical for optimal performance and cost-efficiency. Use the `--instance-type` parameter to specify the GPU instance.

### Example: Deploying Qwen2.5-7B on g5.2xlarge

```bash
emd deploy --model-id Qwen2.5-7B-Instruct --instance-type g5.2xlarge --engine-type vllm --service-type sagemaker_realtime
```

## Achieving Longer Context Windows

To enable longer context windows, use the `--extra-params` option with engine-specific parameters.

### Example: Deploying model with 16k context window

```bash
emd deploy --model-id Qwen2.5-7B-Instruct --instance-type g5.4xlarge --engine-type vllm --service-type sagemaker_realtime --extra-params '{
  "engine_params": {
    "vllm_cli_args": "--max_model_len 16000 --max_num_seqs 4"
  }
}'
```

### Example: Deploying model on G4dn instance

```bash
emd deploy --model-id Qwen2.5-14B-Instruct-AWQ --instance-type g4dn.2xlarge --engine-type vllm --service-type sagemaker_realtime --extra-params '{
  "engine_params": {
    "environment_variables": "export VLLM_ATTENTION_BACKEND=XFORMERS && export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
    "default_cli_args": " --chat-template emd/models/chat_templates/qwen_2d5_add_prefill_chat_template.jinja --max_model_len 12000 --max_num_seqs 10  --gpu_memory_utilization 0.95 --disable-log-stats --enable-auto-tool-choice --tool-call-parser hermes"
  }
}'
```

### Example: Customize model download methods
- You can load models from different locations by addingappropriate values in the extra-params parameter
1. Load model from S3
```json
{
  "model_params":{
    "model_files_s3_path":"<S3_PATH>"
    }
}
```
2. Load model from local path (only applicable for local deployment)
```json
{
  "model_params": {    "model_files_local_path":"<LOCAL_PATH>"
  }
}
```
3. Skip downloading and uploading model files in codebuild, which will significantly reducedeployment time
```json
{
  "model_params": {
    "need_prepare_model":false
  }
}
```
4. Specify the download source for model files
```json
{
  "model_params":{
    "model_files_download_source":"huggingface|modelscope|auto(default)"
    }
}
```
5. Specify the model ID on huggingface or modelscope
```json
{
  "model_params": {
    "huggingface_model_id":"model id on huggingface","modelscope_model_id":"model id on modelscope"
    }
}
```

## Environmental variables
- `LOCAL_DEPLOY_PORT: ` Local deployment port, default: `8080`

## Common Troubleshooting

- If your deployment fails due to out-of-memory issues, try:
  - Using a larger instance type
  - Reducing max_model_len and max_num_seqs in the engine parameters
  - Setting a lower gpu_memory_utilization value (e.g., 0.8 instead of the default)
