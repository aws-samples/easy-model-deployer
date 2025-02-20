<h3 align="center">
Easy Model Deployer - Simple, Efficient, and Easy-to-Integrate
</h3>
---

*Latest News* 🔥

- [2025/03] We officially released EMD! Check out our [blog post](https://vllm.ai).

---

## About

EMD (Easy Model Deployer) is a lightweight tool designed to simplify model deployment. Built for developers who need reliable and scalable model serving without complex setup.

**Key Features**
- One-click deployment of models to the cloud (Amazon SageMaker, Amazon ECS) or on-premises
- Diverse model types (LLMs, VLMs, Embeddings, Vision, etc.)
- Rich inference engine (vLLM, TGI, Lmdeploy, etc.)
- Different instance types (CPU/GPU/AWS Inferentia)
- Convenient integration (OpenAI Compatible API, LangChain client, etc.)

**Notes**

- Please check the [Supported Models](docs/supported_models.md) for complete list.
- OpenAI Compatible API is supported only for Amazon ECS deployment.

## Getting Started

### Installation

Install EMD with `pip`, currently only support for Python 3.9 and above:

```bash
pip install https://github.com/aws-samples/easy-model-deployer/releases/download/v0.1.0/easy_model_deployer-0.1.0-py3-none-any.whl
```

Visit our [documentation](https://aws-samples.github.io/easy-model-deployer/) to learn more.

### Usage

#### Choose your default aws profile.
```bash
emd config set-default-profile-name
```
Notes: If you don't set aws profile, it will use the default profile in your env (suitable for Temporary Credentials). Whenever you want to switch deployment accounts, run ```emd config set-default-profile-name```

#### Bootstrap emd stack
```bash
emd bootstrap
```
Notes: This is going to set up the necessary resources for model deployment. Whenever you change emd version, run this command again.

#### Choose deployment parameters interactively or deploy with one command
```bash
emd deploy
```
Notes: When you see "...waiting for model deployment pipeline...",  it means the deployment task has started, you can quit the current task by ctrl+c.

#### Check deployment status
```bash
emd status
```

#### Quick functional verfication or check our [documentation](https://aws-samples.github.io/easy-model-deployer/) for integration examples.
```bash
emd status
```

#### Delete the deployed model
```bash
emd status
```


## Documentation

For advanced configurations and detailed guides, visit our [documentation site](https://emd-docs.example.com).

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
