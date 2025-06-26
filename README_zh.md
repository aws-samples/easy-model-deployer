<p align="center">
    <h3 align="center">Easy Model Deployer: 大模型上云，一键搞定</h3>
</p>

<p align="center">
  <a href="README.md"><strong>English</strong></a> |
  <a href="README_zh.md"><strong>简体中文</strong></a>
</p>

<p align="center">
  <a href="https://aws-samples.github.io/easy-model-deployer/en/installation"><strong>文档</strong></a> ·
  <a href="https://github.com/aws-samples/easy-model-deployer/releases"><strong>更新日志</strong></a>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellowgreen.svg" alt="MIT License"></a>
  <a href="https://pypi.org/project/easy_model_deployer"><img src="https://img.shields.io/pypi/v/easy_model_deployer.svg?logo=pypi&label=PyPI&logoColor=gold"></a>
  <a href="https://pypi.org/project/easy_model_deployer"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dw/easy_model_deployer"></a>
  <a href="https://github.com/aws-samples/easy-model-deployer/actions/workflows/release-package.yml"><img src="https://github.com/aws-samples/easy-model-deployer/actions/workflows/release-package.yml/badge.svg" alt="Build Status"></a>
</p>

## 🔥 最新动态
- 2024-04-29: 通过[一行命令](https://github.com/aws-samples/easy-model-deployer/blob/main/docs/en/best_deployment_practices.md#famous-models#qwen-3-series)部署 Qwen 3 系列模型。
- 2024-04-21: 通过[一行命令](https://github.com/aws-samples/easy-model-deployer/blob/main/docs/en/best_deployment_practices.md#famous-models#glm-z1-0414-series)部署 GLM Z1/0414 系列模型。
- 2024-03-17: 通过[一行命令](https://github.com/aws-samples/easy-model-deployer/blob/main/docs/en/best_deployment_practices.md#famous-models#gemma-3-series)部署 Gemma 3 系列模型。
- 2024-03-06: 通过[一行命令](https://github.com/aws-samples/easy-model-deployer/blob/main/docs/en/best_deployment_practices.md#famous-models#qwen-series#qwq-32b)部署 QwQ-32B。

## 简介

还在为大模型部署而头疼吗？Easy Model Deployer 让你告别复杂的环境配置，轻松将**开源大模型**（[支持的模型](docs/en/supported_models.md)）部署到 AWS 云端。

无论是大语言模型、视觉模型还是自定义模型，一条命令即可搞定部署。更棒的是，部署完成后直接获得 **OpenAI 兼容 API** 和 [**LangChain 接口**](https://github.com/langchain-ai/langchain)，让你的 AI 应用开发如虎添翼。

专为追求高效、稳定模型服务的开发者打造，让技术门槛不再成为创新的阻碍。

![cli](docs/images/demo.avif)

**核心特性**

- 一键部署模型到 AWS（Amazon SageMaker、Amazon ECS、Amazon EC2）
- 多样化模型类型（大语言模型、视觉语言模型、嵌入模型、视觉模型等）
- 丰富的推理引擎（vLLM、TGI、Lmdeploy 等）
- 不同实例类型（CPU/GPU/AWS Inferentia）
- 便捷集成（OpenAI 兼容 API、LangChain 客户端等）

## 支持的模型

Easy Model Deployer 支持广泛的模型类型，包括：

- **大语言模型**: Qwen、Llama、DeepSeek、GLM、InternLM、Baichuan 等
- **视觉语言模型**: Qwen-VL、InternVL、Gemma3-Vision 等
- **嵌入模型**: BGE、Jina、基于 BERT 的模型
- **重排序模型**: BGE-Reranker、Jina-Reranker
- **语音识别模型**: Whisper 变体
- **自定义模型**: 支持自定义 Docker 镜像

完整的支持模型列表和部署配置，请参见[支持的模型](docs/en/supported_models.md)。

## 🔧 快速开始

### 安装

通过 PyPI 安装 Easy Model Deployer，目前支持 Python 3.9 及以上版本：

```bash
pip install easy-model-deployer
emd
```

### 初始化

准备模型部署所需的基础资源。

更多信息请参考[架构说明](https://aws-samples.github.io/easy-model-deployer/en/architecture/)。

```bash
emd bootstrap
```

> **💡 提示** 通过 `pip` 升级 EMD 后，需要重新运行此命令来更新环境。

### 部署模型

通过交互式 CLI 或一行命令部署模型。

```bash
emd deploy
```

> **💡 提示** 要查看所有可用参数，请运行 `emd deploy --help`。
> 当您看到 "Waiting for model: ..." 消息时，表示部署任务已开始，您可以按 `Ctrl+C` 停止终端输出。
>
> - 有关部署参数的更多信息，请参考[部署参数](docs/en/installation.md)。
> - 有关使用命令行参数的最佳实践示例，请参考[最佳部署实践](docs/en/best_deployment_practices.md)。

### 查看状态

检查模型部署任务的状态。

```bash
emd status
```

> **💡 提示** EMD 允许同时启动多个部署任务。

### 调用模型

通过 CLI 调用已部署的模型进行测试。

```bash
emd invoke <ModelId>
```

> **💡 提示** 您可以在 `emd status` 的输出中找到 *ModelId*。例如：`emd invoke DeepSeek-R1-Distill-Qwen-1.5B`

- [集成示例](https://aws-samples.github.io/easy-model-deployer/)
- [EMD 客户端](docs/en/emd_client.md)
- [Langchain 接口](docs/en/langchain_interface.md)
- [OpenAI 兼容接口](docs/en/openai_compatiable.md)

> **💡 提示** OpenAI 兼容 API 仅支持 Amazon ECS 和 Amazon EC2 部署类型。

### 列出支持的模型

快速查看支持哪些模型，此命令将输出与部署相关的所有信息。（更多信息请浏览[支持的模型](docs/en/supported_models.md)。）

```bash
emd list-supported-models
```

### 删除模型

删除已部署的模型。

```bash
emd destroy <ModelId>
```

> **💡 提示** 您可以在 `emd status` 的输出中找到 *ModelId*。例如：`emd destroy DeepSeek-R1-Distill-Qwen-1.5B`

## 📖 文档

有关高级配置和详细指南，请访问我们的[文档网站](https://aws-samples.github.io/easy-model-deployer/)。

## 🤝 贡献

我们欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

