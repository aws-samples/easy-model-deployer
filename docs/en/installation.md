## Installation Guide

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### Setting up the Environment

1. Create a virtual environment:
```bash
python -m venv emd-env
```

2. Activate the virtual environment:
```bash
source emd-env/bin/activate
```

3. Install the required packages:
```bash
pip install https://github.com/aws-samples/easy-model-deployer/releases/download/emd-0.7.1/emd-0.7.1-py3-none-any.whl
```


## Deployment parameters

### --force-update-env-stack
No additional ```emd bootstrap``` required for deployment. Because of other commands, status/destroy etc. require pre-bootstrapping. Therefore, it is recommended to run ```emd bootstrap``` separately after each upgrade.

### --extra-params
Extra parameters passed to the model deployment. extra-params should be a Json object of dictionary format as follows:

```json
{

  "model_params": {
  },
  "service_params":{
  },
  "instance_params":{
  },
  "engine_params":{
      "cli_args": "<command line arguments of current engine>",
      "api_key":"<api key>"
  },
  "framework_params":{
      "uvicorn_log_level":"info",
      "limit_concurrency":200
  }
}
```
To learn some practice examples, please refer to the [Best Deployment Practices](https://aws-samples.github.io/easy-model-deployer/en/best_deployment_practices/).



## Local deployment on the ec2 instance

This is suitable for deploying models using local GPU resources.

### Pre-requisites

#### Start and connect to EC2 instance

It is recommended to launch the instance using the AMI "**Deep Learning OSS Nvidia Driver AMI GPU PyTorch 2.6 (Ubuntu 22.04)**".


### Deploy model using EMD

```sh
emd deploy --allow-local-deploy
```

There some EMD configuration sample settings for model deployment in the following two sections: [Non-reasoning Model deployment configuration](#non-reasoning-model-deployment-configuration) and [Reasoning Model deployment configuration](#reasoning-model-deployment-configuration).
Wait for the model deployment to complete.

#### Non-reasoning Model deployment configuration

##### Qwen2.5-72B-Instruct-AWQ

```
? Select the model series: qwen2.5
? Select the model name: Qwen2.5-72B-Instruct-AWQ
? Select the service for deployment: Local
? input the local gpu ids to deploy the model (e.g. 0,1,2): 0,1,2,3
? Select the inference engine to use: tgi
? (Optional) Additional deployment parameters (JSON string or local file path), you can skip by pressing Enter: {"engine_params":{"api_key":"<YOUR_API_KEY>", "default_cli_args": "--max-total-tokens 30000 --max-concurrent-requests 30"}}
```

##### llama-3.3-70b-instruct-awq
```
? Select the model series: llama
? Select the model name: llama-3.3-70b-instruct-awq
? Select the service for deployment: Local
? input the local gpu ids to deploy the model (e.g. 0,1,2): 0,1,2,3
engine type: tgi
framework type: fastapi
? (Optional) Additional deployment parameters (JSON string or local file path), you can skip by pressing Enter: {"engine_params":{"api_key":"<YOUR_API_KEY>", "default_cli_args": "--max-total-tokens 30000 --max-concurrent-requests 30"}}
```

#### Reasoning Model deployment configuration

##### DeepSeek-R1-Distill-Qwen-32B
```
? Select the model series: deepseek reasoning model
? Select the model name: DeepSeek-R1-Distill-Qwen-32B
? Select the service for deployment: Local
? input the local gpu ids to deploy the model (e.g. 0,1,2): 0,1,2,3
engine type: vllm
framework type: fastapi
? (Optional) Additional deployment parameters (JSON string or local file path), you can skip by pressing Enter: {"engine_params":{"api_key":"<YOUR_API_KEY>", "default_cli_args": "--enable-reasoning --reasoning-parser deepseek_r1 --max_model_len 16000 --disable-log-stats --chat-template emd/models/chat_templates/deepseek_r1_distill.jinja --max_num_seq 20 --gpu_memory_utilization 0.9"}}
```

##### deepseek-r1-distill-llama-70b-awq

```
? Select the model series: deepseek reasoning model
? Select the model name: deepseek-r1-distill-llama-70b-awq
? Select the service for deployment: Local
? input the local gpu ids to deploy the model (e.g. 0,1,2): 0,1,2,3
? Select the inference engine to use: tgi
framework type: fastapi
? (Optional) Additional deployment parameters (JSON string or local file path), you can skip by pressing Enter: {"engine_params":{"api_key":"<YOUR_API_KEY>", "default_cli_args": "--max-total-tokens 30000 --max-concurrent-requests 30"}}
```

## Examples
