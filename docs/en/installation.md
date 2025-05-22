# Quick Start Guide

This guide provides simple step-by-step instructions for using Easy Model Deployer (EMD).

## Prerequisites

Before installing Easy Model Deployer, ensure your environment meets the following requirements:

| Requirement | Details |
|-------------|---------|
| **Python** | Version 3.9 or higher required. EMD leverages modern Python features for optimal performance. |
| **pip** | The Python package installer must be available to install EMD and its dependencies. |
| **AWS Account** | Required for deploying models to AWS services (SageMaker, ECS, EC2). |
| **AWS CLI** | Configured with appropriate credentials and permissions for resource creation. |
| **Internet Connection** | Required for downloading model artifacts and dependencies. |

For local deployments, additional requirements apply. See the [Local Deployment Guide](local_deployment.md) for details.

## Installation

**Optional: Create a Virtual Environment**

It's recommended to install EMD in a virtual environment to avoid conflicts with other Python packages:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

After activating the virtual environment, your terminal prompt should change to indicate the active environment. You can then proceed with installation.

Easy Model Deployer can be installed using various package managers. Choose the method that best suits your workflow:

**Using pip:**
```bash
pip install easy-model-deployer
```

**Using pipx:**
```bash
# Install pipx if you don't have it
pip install --user pipx
pipx ensurepath

# Install EMD
pipx install easy-model-deployer
```

**Using uv:**
```bash
# Install uv if you don't have it
pip install uv

# Install EMD
uv pip install easy-model-deployer
```

**Verification:**
After installation, verify that EMD is working correctly by running:
```bash
emd version
```
This should display the installed version of Easy Model Deployer.

**Upgrading:**
To upgrade to the latest version:

```bash
# Using pip
pip install --upgrade easy-model-deployer

# Using pipx
pipx upgrade easy-model-deployer

# Using uv
uv pip install --upgrade easy-model-deployer
```

> **Note**: After upgrading, you should run `emd bootstrap` again to ensure your environment is updated.

## Bootstrap

Before deploying models, you need to bootstrap the environment:

```bash
emd bootstrap
```

> **Note**: You need to run this command again after upgrading EMD with pip to update the environment.

## Deploy a Model

Deploy a model using the interactive CLI:

```bash
emd deploy
```

The CLI will guide you through selecting:
- Model series
- Specific model
- Deployment service (SageMaker, ECS, EC2, or Local)
- Instance type or GPU IDs
- Inference engine
- Additional parameters

You can also deploy models directly with command line parameters:

```bash
emd deploy --model-series llama --model-name llama-3.3-70b-instruct-awq --service SageMaker
```

For secure API access, you can configure an API key during deployment using the `--extra-params` option:

```bash
emd deploy --model-id <model-id> --instance-type <instance-type> --engine-type <engine-type> --service-type <service-type> --extra-params '{
  "service_params": {
    "api_key": "your-secure-api-key"
  }
}'
```

When using the interactive CLI (`emd deploy`), you can also provide this JSON configuration in the "Extra Parameters" step of the deployment process. Simply paste the JSON structure when prompted for additional parameters:

```json
{
  "service_params": {
    "api_key": "your-secure-api-key"
  }
}
```

This API key will be required for authentication when accessing your deployed model's endpoint, enhancing security for your inference services.

> **Note**: For local deployment options and detailed model configurations, see the [Local Deployment Guide](local_deployment.md).

## Check Deployment Status

Monitor the status of your deployment:

```bash
emd status
```

This command shows all active deployments with their ModelIds, endpoints, and status.

## Invoke the Model

Test your deployed model using the CLI:

```bash
emd invoke <ModelId>
```

Replace `<ModelId>` with the ID shown in the status output.

## Integration Options

EMD provides an OpenAI-compatible API that allows you to integrate with your deployed models using standard tools and libraries:

- **OpenAI Compatible API**: The primary integration method using the OpenAI API format. Once you have the base URL and API key from the `emd status` command, you can access the API using the OpenAI SDK or any OpenAI-compatible client. [API Documentation](api.md)
- **EMD Client**: For direct Python integration
- **LangChain Interface**: For integration with LangChain applications

The API uses an OpenAI-compatible format, making it easy to switch between OpenAI's services and your deployed models with minimal code changes.

## Destroy the Deployment

When you no longer need the model, remove the deployment:

```bash
emd destroy <ModelId>
```

Replace `<ModelId>` with the ID shown in the status output.

## Advanced Options

For more detailed information on:

- Advanced deployment parameters: See [Best Deployment Practices](https://aws-samples.github.io/easy-model-deployer/en/best_deployment_practices/)
- Architecture details: See [Architecture](https://aws-samples.github.io/easy-model-deployer/en/architecture/)
- Supported models: See [Supported Models](https://aws-samples.github.io/easy-model-deployer/en/supported_models/)
- Local deployment: See [Local Deployment Guide](local_deployment.md)
- CLI commands reference: See [CLI Commands](commands.md)
- API documentation: See [API Documentation](api.md)
