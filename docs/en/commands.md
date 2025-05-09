# CLI Commands

This document provides a comprehensive guide to the command-line interface (CLI) commands available in the Easy Model Deployer (EMD) tool.

## Overview

EMD provides the following main commands:

| Command | Description |
|---------|-------------|
| `bootstrap` | Initialize AWS resources for model deployment |
| `deploy` | Deploy models to AWS infrastructure |
| `status` | Display status of deployed models |
| `invoke` | Test deployed models with sample requests |
| `example` | Generate sample code for API integration |
| `destroy` | Remove deployed models and clean up resources |
| `list-supported-models` | Display available models |
| `profile` | Configure AWS profile credentials |
| `version` | Display tool version information |

## Command Details

### bootstrap

Initialize AWS resources required for model deployment.

```bash
emd bootstrap [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--skip-confirm` | Skip confirmation prompts |

**Example:**

```bash
emd bootstrap
```

This command creates the necessary AWS resources, including an S3 bucket and CloudFormation stack, required for model deployment.

### deploy

Deploy models to AWS infrastructure.

```bash
emd deploy [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--model-id TEXT` | Model ID to deploy |
| `-i, --instance-type TEXT` | The instance type to use |
| `-e, --engine-type TEXT` | The name of the inference engine |
| `-s, --service-type TEXT` | The name of the service |
| `--framework-type TEXT` | The name of the framework |
| `--model-tag TEXT` | Custom tag for the model deployment |
| `--extra-params TEXT` | Extra parameters in JSON format |
| `--skip-confirm` | Skip confirmation prompts |
| `--force-update-env-stack` | Force update environment stack |
| `--allow-local-deploy` | Allow local instance deployment |
| `--only-allow-local-deploy` | Only allow local instance deployment |
| `--dockerfile-local-path TEXT` | Custom Dockerfile path for building the model image |
| `--local-gpus TEXT` | Local GPU IDs to deploy the model (e.g., `0,1,2`) |

**Examples:**

Deploy a model with interactive prompts:
```bash
emd deploy
```

Deploy a specific model with parameters:
```bash
emd deploy --model-id Qwen2.5-7B-Instruct --instance-type g5.2xlarge --engine-type vllm --service-type sagemaker_realtime
```

Deploy a model locally:
```bash
emd deploy --allow-local-deploy
```

Deploy with custom parameters:
```bash
emd deploy --model-id Qwen2.5-7B-Instruct --extra-params '{"engine_params": {"vllm_cli_args": "--max_model_len 16000 --max_num_seqs 4"}}'
```

### status

Display the status of deployed models.

```bash
emd status [MODEL_ID] [MODEL_TAG]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `MODEL_ID` | Optional model ID to check status for |
| `MODEL_TAG` | Optional model tag (defaults to "dev") |

**Examples:**

Check status of all deployed models:
```bash
emd status
```

Check status of a specific model:
```bash
emd status Qwen2.5-7B-Instruct
```

Check status of a specific model with a custom tag:
```bash
emd status Qwen2.5-7B-Instruct custom-tag
```

### invoke

Test deployed models with sample requests.

```bash
emd invoke MODEL_ID [MODEL_TAG]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `MODEL_ID` | Model ID to invoke |
| `MODEL_TAG` | Optional model tag (defaults to "dev") |

**Examples:**

Invoke a model:
```bash
emd invoke DeepSeek-R1-Distill-Qwen-7B
```

Invoke a model with a custom tag:
```bash
emd invoke DeepSeek-R1-Distill-Qwen-7B custom-tag
```

### example

Generate sample code for API integration with a deployed model.

```bash
emd example MODEL_ID/MODEL_TAG
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `MODEL_ID/MODEL_TAG` | Model ID and optional tag (separated by "/") |

**Examples:**

Generate examples for a model:
```bash
emd example Qwen2.5-7B-Instruct
```

Generate examples for a model with a custom tag:
```bash
emd example Qwen2.5-7B-Instruct/custom-tag
```

### destroy

Remove deployed models and clean up resources.

```bash
emd destroy MODEL_ID [MODEL_TAG]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `MODEL_ID` | Model ID to destroy |
| `MODEL_TAG` | Optional model tag (defaults to "dev") |

**Examples:**

Destroy a model:
```bash
emd destroy Qwen2.5-7B-Instruct
```

Destroy a model with a custom tag:
```bash
emd destroy Qwen2.5-7B-Instruct custom-tag
```

### list-supported-models

Display available models that can be deployed.

```bash
emd list-supported-models [MODEL_ID] [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `MODEL_ID` | Optional model ID to filter results |

**Options:**

| Option | Description |
|--------|-------------|
| `-a, --detail` | Output model information in detail |

**Examples:**

List all supported models:
```bash
emd list-supported-models
```

List detailed information for all models:
```bash
emd list-supported-models --detail
```

List information for a specific model:
```bash
emd list-supported-models Qwen2.5-7B-Instruct
```

### profile

Configure AWS profile credentials for deployment.

```bash
emd profile COMMAND [ARGS]
```

**Commands:**

| Command | Description |
|---------|-------------|
| `set-default-profile-name [NAME]` | Set the default profile name for deployment |
| `show-default-profile-name` | Show current default profile |
| `remove-default-profile-name` | Remove the default profile |

**Examples:**

Set a default AWS profile:
```bash
emd profile set-default-profile-name my-profile
```

Show the current default profile:
```bash
emd profile show-default-profile-name
```

Remove the default profile:
```bash
emd profile remove-default-profile-name
```

### version

Display the current version of the EMD tool.

```bash
emd version
```

**Example:**

```bash
emd version
```

## Environment Variables

- `LOCAL_DEPLOY_PORT`: Local deployment port (default: `8080`)

## Additional Resources

- [Installation Guide](installation.md)
- [Best Deployment Practices](best_deployment_practices.md)
- [Supported Models](supported_models.md)
- [Langchain Interface](langchain_interface.md)
