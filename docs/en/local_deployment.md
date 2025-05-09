# Local Model Deployment Guide

This guide provides detailed instructions for deploying models locally using Easy Model Deployer (EMD).

## Local Deployment on EC2 Instance

For deploying models using local GPU resources:

### Prerequisites

It is recommended to launch an EC2 instance using the AMI "**Deep Learning OSS Nvidia Driver AMI GPU PyTorch 2.6 (Ubuntu 22.04)**".

### Deployment Command

Deploy with:

```bash
emd deploy --allow-local-deploy
```

## Command Line Deployment

You can deploy models directly with command line parameters:

```bash
emd deploy --model-series llama --model-name llama-3.3-70b-instruct-awq --service Local --gpu-ids 0,1,2,3
```

## Additional Parameters

You can provide additional parameters as a JSON string:

```bash
emd deploy --extra-params '{"engine_params":{"api_key":"YOUR_API_KEY", "default_cli_args": "--max-total-tokens 30000 --max-concurrent-requests 30"}}'
```

Or from a file:

```bash
emd deploy --extra-params path/to/params.json
```

The extra parameters format:

```json
{
  "model_params": {
  },
  "service_params":{
  },
  "instance_params":{
  },
  "engine_params":{
      "cli_args": "<command line arguments of current engine>"
  },
  "framework_params":{
      "uvicorn_log_level":"info",
      "limit_concurrency":200
  }
}
```

## Common Model Configurations

### Non-reasoning Models

#### Qwen2.5-72B-Instruct-AWQ

```
? Select the model series: qwen2.5
? Select the model name: Qwen2.5-72B-Instruct-AWQ
? Select the service for deployment: Local
? input the local gpu ids to deploy the model (e.g. 0,1,2): 0,1,2,3
? Select the inference engine to use: tgi
? (Optional) Additional deployment parameters: {"engine_params":{"api_key":"<YOUR_API_KEY>", "default_cli_args": "--max-total-tokens 30000 --max-concurrent-requests 30"}}
```

#### llama-3.3-70b-instruct-awq

```
? Select the model series: llama
? Select the model name: llama-3.3-70b-instruct-awq
? Select the service for deployment: Local
? input the local gpu ids to deploy the model (e.g. 0,1,2): 0,1,2,3
? Select the inference engine to use: tgi
? (Optional) Additional deployment parameters: {"engine_params":{"api_key":"<YOUR_API_KEY>", "default_cli_args": "--max-total-tokens 30000 --max-concurrent-requests 30"}}
```

### Reasoning Models

#### DeepSeek-R1-Distill-Qwen-32B

```
? Select the model series: deepseek reasoning model
? Select the model name: DeepSeek-R1-Distill-Qwen-32B
? Select the service for deployment: Local
? input the local gpu ids to deploy the model (e.g. 0,1,2): 0,1,2,3
? Select the inference engine to use: vllm
? (Optional) Additional deployment parameters: {"engine_params":{"api_key":"<YOUR_API_KEY>", "default_cli_args": "--enable-reasoning --reasoning-parser deepseek_r1 --max_model_len 16000 --disable-log-stats --chat-template emd/models/chat_templates/deepseek_r1_distill.jinja --max_num_seq 20 --gpu_memory_utilization 0.9"}}
```

#### deepseek-r1-distill-llama-70b-awq

```
? Select the model series: deepseek reasoning model
? Select the model name: deepseek-r1-distill-llama-70b-awq
? Select the service for deployment: Local
? input the local gpu ids to deploy the model (e.g. 0,1,2): 0,1,2,3
? Select the inference engine to use: tgi
? (Optional) Additional deployment parameters: {"engine_params":{"api_key":"<YOUR_API_KEY>", "default_cli_args": "--max-total-tokens 30000 --max-concurrent-requests 30"}}
```

## Tips for Local Deployment

- When you see "Waiting for model: ...", it means the deployment task has started. You can press `Ctrl+C` to stop the terminal output without affecting the deployment.
- For multi-GPU deployments, ensure all specified GPUs are available and have sufficient memory.
- Monitor GPU usage with tools like `nvidia-smi` during deployment and inference.
- For optimal performance, consider the recommended GPU memory requirements for each model.

## Advanced Options

For more detailed information on:
- Advanced deployment parameters: See [Best Deployment Practices](https://aws-samples.github.io/easy-model-deployer/en/best_deployment_practices/)
- Architecture details: See [Architecture](https://aws-samples.github.io/easy-model-deployer/en/architecture/)
- Supported models: See [Supported Models](https://aws-samples.github.io/easy-model-deployer/en/supported_models/)
