<h3 align="center">
Easy Model Deployer - Simple, Efficient, and Easy-to-Integrate
</h3>

---

![cli](docs/images/cli.gif)

---

## Introduction

Easy Model Deployer is a lightweight tool designed to simplify model deployment. Built for developers who need reliable and scalable model serving without complex setup.

**Supported Models**

For a detailed list of supported models, please refer to [Supported Models](docs/en/supported_models.md)

**Key Features**
- One-click deployment of models to the cloud (Amazon SageMaker, Amazon ECS, Amazon EC2)
- Diverse model types (LLMs, VLMs, Embeddings, Vision, etc.)
- Rich inference engine (vLLM, TGI, Lmdeploy, etc.)
- Different instance types (CPU/GPU/AWS Inferentia)
- Convenient integration (OpenAI Compatible API, LangChain client, etc.)

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)
- [Contributing](#contributing)


## Getting Started

### Installation

Install EMD with `pip`, currently support for Python 3.9 and above:

```bash
pip install https://github.com/aws-samples/easy-model-deployer/releases/download/emd-0.7.1/emd-0.7.1-py3-none-any.whl
```

Visit our [documentation](https://aws-samples.github.io/easy-model-deployer/en/installation/) to learn more.

### Usage

#### Set AWS Profile
```bash
emd config set-default-profile-name
```
> **Note:** If you don't set AWS profile, EMD will use the default profile in your environment (suitable for Temporary Credentials). Whenever you want to change the profile, you can run this command again.

![config](docs/images/emd-config.png)

#### Bootstrap

Setting up necessary resources for model deployment.

```bash
emd bootstrap
```

> **Note:** Once you upgrade the EMD, you need to run this command again.


#### Deploy Models

Deploy models with an interactive CLI or one command.

```bash
emd deploy
```

![deploy](docs/images/emd-deploy.png)


> **Note:** To view all available parameters, run `emd deploy --help`.
> When you see the message "Waiting for model: ...", it means the deployment task has started and you can stop the terminal output by pressing `Ctrl+C`.
> For more information on deployment parameters, please refer to the [Deployment parameters](docs/en/deployment.md).

#### List Supported Models

Quickly see what models are supported, this command will output all information related to deployment. (Plese browse [Supported Models](docs/en/supported_models.md) for more information.)

```bash
emd list-supported-models
```

The following command is recommended to just list the model types.

```bash
emd list-supported-models | jq -r '.[] | "\(.model_id)\t\(.model_type)"' | column -t -s $'\t' | sort


#### Deployment Status

Check the status of the model deployment task.

```bash
emd status
```

![alt text](docs/images/emd-status.png)

> **Note:** The EMD allows launch multiple deployment tasks simultaneously.

#### Quick invocation

Invoke the deployed model for testing by CLI.

```bash
emd invoke DeepSeek-R1-Distill-Qwen-1.5B
```

![alt text](docs/images/emd-invoke.png)

> **Note:** You can find the *ModelId* in the output by `emd status`.

- [Integration examples](https://aws-samples.github.io/easy-model-deployer/)
- [EMD client](docs/en/emd_client.md)
- [Langchain interface](docs/en/langchain_interface.md)
- [OpenAI compatible interface](docs/en/openai_compatiable.md).

> **Notes** OpenAI Compatible API is supported only for Amazon ECS and Amazon EC2 deployment types.

#### Delete Model

Delete the deployed model.

```bash
emd destroy DeepSeek-R1-Distill-Qwen-1.5B
```

> **Note:** You can find the *ModelId* in the output by `emd status`.

```

## Documentation

For advanced configurations and detailed guides, visit our [documentation site](https://aws-samples.github.io/easy-model-deployer/).


## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
