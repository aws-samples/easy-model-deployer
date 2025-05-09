# Best Deployment Practices

This document provides examples of best practices for deploying models using EMD for various use cases.

## Example Model Deployments
### Qwen 3 Series
```
emd deploy --model-id Qwen3-30B-A3B --instance-type g5.12xlarge --engine-type vllm --service-type sagemaker_realtime

emd deploy --model-id Qwen3-32B --instance-type g5.12xlarge --engine-type vllm --service-type sagemaker_realtime

emd deploy --model-id Qwen3-8B --instance-type g5.12xlarge --engine-type vllm --service-type sagemaker_realtime
```


### GLM Z1/0414 Series
```
emd deploy --model-id GLM-Z1-32B-0414 --instance-type g5.12xlarge --engine-type vllm --service-type sagemaker_realtime

emd deploy --model-id GLM-4-32B-0414 --instance-type g5.12xlarge --engine-type vllm --service-type sagemaker_realtime
```


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

## Extra Parameters Usage

The `--extra-params` option allows you to customize various aspects of your deployment. This section provides a detailed reference for the available parameters organized by category.

### Parameter Structure

The extra parameters are structured as a JSON object with the following top-level categories:

```json
{
  "model_params": {},
  "service_params": {},
  "instance_params": {},
  "engine_params": {},
  "framework_params": {}
}
```

### Model Parameters

Model parameters control how the model is loaded and prepared.

#### Model Source Configuration

```json
{
  "model_params": {
    "model_files_s3_path": "s3://your-bucket/model-path",
    "model_files_local_path": "/path/to/local/model",
    "model_files_download_source": "huggingface|modelscope|auto",
    "huggingface_model_id": "organization/model-name",
    "modelscope_model_id": "organization/model-name",
    "need_prepare_model": false
  }
}
```

- `model_files_s3_path`: Load model directly from an S3 path
- `model_files_local_path`: Load model from a local path (only for local deployment)
- `model_files_download_source`: Specify the source for downloading model files
- `huggingface_model_id`: Specify a custom Hugging Face model ID
- `modelscope_model_id`: Specify a custom ModelScope model ID
- `need_prepare_model`: Set to `false` to skip downloading and uploading model files (reduces deployment time)

### Service Parameters

Service parameters configure the deployment service behavior.

#### API Security

```json
{
  "service_params": {
    "api_key": "your-secure-api-key"
  }
}
```

- `api_key`: Set a custom API key for securing access to your model endpoint

#### SageMaker-specific Parameters

```json
{
  "service_params": {
    "max_capacity": 2,
    "min_capacity": 1,
    "auto_scaling_target_value": 15,
    "sagemaker_endpoint_name": "custom-endpoint-name"
  }
}
```

- `max_capacity`: Maximum number of instances for auto-scaling
- `min_capacity`: Minimum number of instances for auto-scaling
- `auto_scaling_target_value`: Target value for auto-scaling (in requests per minute)
- `sagemaker_endpoint_name`: Custom name for the SageMaker endpoint

#### ECS-specific Parameters

```json
{
  "service_params": {
    "desired_capacity": 2,
    "max_size": 4,
    "vpc_id": "vpc-12345",
    "subnet_ids": "subnet-12345,subnet-67890"
  }
}
```

- `desired_capacity`: Desired number of ECS tasks
- `max_size`: Maximum number of ECS tasks for auto-scaling
- `vpc_id`: Custom VPC ID for deployment
- `subnet_ids`: Comma-separated list of subnet IDs

### Engine Parameters

Engine parameters control the behavior of the inference engine.

#### Common Engine Parameters

```json
{
  "engine_params": {
    "environment_variables": "export VAR1=value1 && export VAR2=value2",
    "cli_args": "--specific-engine-arg value",
    "default_cli_args": "--common-engine-arg value"
  }
}
```

- `environment_variables`: Set environment variables for the engine
- `cli_args`: Specific command line arguments for the engine
- `default_cli_args`: Default command line arguments for the engine

#### vLLM-specific Parameters

```json
{
  "engine_params": {
    "vllm_cli_args": "--max_model_len 16000 --max_num_seqs 4 --gpu_memory_utilization 0.9",
    "environment_variables": "export VLLM_ATTENTION_BACKEND=FLASHINFER && export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
  }
}
```

- `vllm_cli_args`: Command line arguments specific to vLLM
- Common vLLM parameters:
  - `--max_model_len`: Maximum context length
  - `--max_num_seqs`: Maximum number of sequences
  - `--gpu_memory_utilization`: GPU memory utilization (0.0-1.0)
  - `--disable-log-stats`: Disable logging of statistics
  - `--enable-auto-tool-choice`: Enable automatic tool choice
  - `--tool-call-parser`: Specify tool call parser (e.g., hermes, pythonic)
  - `--enable-reasoning`: Enable reasoning capabilities
  - `--reasoning-parser`: Specify reasoning parser (e.g., deepseek_r1, granite)
  - `--chat-template`: Path to chat template file

#### TGI-specific Parameters

```json
{
  "engine_params": {
    "default_cli_args": "--max-total-tokens 30000 --max-concurrent-requests 30"
  }
}
```

- Common TGI parameters:
  - `--max-total-tokens`: Maximum total tokens
  - `--max-concurrent-requests`: Maximum concurrent requests
  - `--max-batch-size`: Maximum batch size
  - `--max-input-tokens`: Maximum input tokens

### Framework Parameters

Framework parameters configure the web framework serving the model.

#### FastAPI Parameters

```json
{
  "framework_params": {
    "limit_concurrency": 200,
    "timeout_keep_alive": 120,
    "uvicorn_log_level": "info"
  }
}
```

- `limit_concurrency`: Maximum number of concurrent connections
- `timeout_keep_alive`: Timeout for keeping connections alive (in seconds)
- `uvicorn_log_level`: Log level for Uvicorn server (debug, info, warning, error, critical)

### Example Configurations

#### Example: High-throughput Configuration

```json
{
  "engine_params": {
    "default_cli_args": "--max_model_len 8000 --max_num_seqs 20 --gpu_memory_utilization 0.95"
  },
  "framework_params": {
    "limit_concurrency": 500,
    "timeout_keep_alive": 30
  },
  "service_params": {
    "max_capacity": 3,
    "min_capacity": 1,
    "auto_scaling_target_value": 20
  }
}
```

#### Example: Long Context Configuration

```json
{
  "engine_params": {
    "default_cli_args": "--max_model_len 32000 --max_num_seqs 2 --gpu_memory_utilization 0.9"
  },
  "service_params": {
    "api_key": "your-secure-api-key"
  }
}
```

#### Example: Secure API with Custom Endpoint Name

```json
{
  "service_params": {
    "api_key": "your-secure-api-key",
    "sagemaker_endpoint_name": "my-custom-llm-endpoint"
  }
}
```

### Model Source Configuration

You can load models from different locations by adding appropriate values in the extra-params parameter:

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
3. Skip downloading and uploading model files in codebuild, which will significantly reduce deployment time
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

This section covers common issues you might encounter during model deployment and their solutions.

### Memory-Related Issues

If your deployment fails with out-of-memory (OOM) errors:

```
CUDA out of memory. Tried to allocate X.XX GiB
```

Try these solutions:

1. **Use a larger instance type**:
   - Upgrade to an instance with more GPU memory (e.g., from g5.2xlarge to g5.4xlarge)
   - For large models (>30B parameters), consider using multiple GPUs with g5.12xlarge or g5.48xlarge

2. **Adjust engine parameters**:
   ```json
   {
     "engine_params": {
       "default_cli_args": "--max_model_len 8000 --max_num_seqs 4 --gpu_memory_utilization 0.8"
     }
   }
   ```
   - Reduce `max_model_len` to decrease context window size
   - Lower `max_num_seqs` to reduce concurrent sequences
   - Set `gpu_memory_utilization` to a lower value (e.g., 0.8 instead of the default 0.9)

3. **Use quantized models**:
   - Deploy AWQ or GPTQ quantized versions of models (e.g., Qwen2.5-7B-Instruct-AWQ instead of Qwen2.5-7B-Instruct)

### Deployment Timeout Issues

If your deployment times out during model preparation:

1. **Skip model preparation**:
   ```json
   {
     "model_params": {
       "need_prepare_model": false
     }
   }
   ```

2. **Use pre-downloaded models**:
   ```json
   {
     "model_params": {
       "model_files_s3_path": "s3://your-bucket/model-path"
     }
   }
   ```

### API Connection Issues

If you can't connect to your deployed model's API:

1. **Check endpoint status**:
   ```bash
   emd status
   ```
   Ensure the status is "InService" or "Running"

2. **Verify API key**:
   - Ensure you're using the correct API key in your requests
   - If you've set a custom API key, make sure to include it in your requests

3. **Test with curl**:
   ```bash
   curl -X POST https://your-endpoint.execute-api.region.amazonaws.com/v1/chat/completions \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your-api-key" \
     -d '{"model": "your-model-id", "messages": [{"role": "user", "content": "Hello"}]}'
   ```

### Performance Optimization

If your model is running slowly:

1. **Increase GPU utilization**:
   ```json
   {
     "engine_params": {
       "default_cli_args": "--gpu_memory_utilization 0.95"
     }
   }
   ```

2. **Adjust batch size and concurrency**:
   ```json
   {
     "engine_params": {
       "default_cli_args": "--max_num_seqs 20"
     },
     "framework_params": {
       "limit_concurrency": 200
     }
   }
   ```

3. **Enable optimizations** (for vLLM):
   ```json
   {
     "engine_params": {
       "environment_variables": "export VLLM_ATTENTION_BACKEND=FLASHINFER && export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
     }
   }
   ```
