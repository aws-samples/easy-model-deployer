# Dify Integration

This guide covers how to integrate EMD-deployed models with [Dify](https://github.com/langgenius/dify), an open-source LLM app development platform.

## Overview

Dify is a comprehensive LLM app development platform that combines workflow automation, RAG pipeline, agent capabilities, model management, and observability features. With its intuitive interface, you can quickly build AI applications using models deployed with Easy Model Deployer (EMD).

With Dify, you can:
- Create AI applications with visual workflows
- Connect to various LLM providers, including custom OpenAI API-compatible endpoints
- Build RAG (Retrieval-Augmented Generation) pipelines
- Create AI agents with tools and function calling
- Monitor and analyze application performance
- Deploy your applications with ready-to-use APIs

## Key Features of Dify

- **Workflow**: Build and test AI workflows on a visual canvas
- **Comprehensive Model Support**: Integration with hundreds of proprietary and open-source LLMs
- **Prompt IDE**: Intuitive interface for crafting prompts and comparing model performance
- **RAG Pipeline**: Extensive capabilities for document ingestion and retrieval
- **Agent Capabilities**: Define agents with LLM Function Calling or ReAct, with 50+ built-in tools
- **LLMOps**: Monitor and analyze application logs and performance
- **Backend-as-a-Service**: APIs for integrating Dify into your business logic

## Integrating EMD Models with Dify

EMD-deployed models can be easily integrated with Dify through its OpenAI API-compatible interface. This allows you to use your own deployed models with all the features and capabilities of the Dify platform.

### Prerequisites

1. You have successfully deployed a model using EMD with the OpenAI Compatible API enabled
2. You have installed Dify (either using [Dify Cloud](https://cloud.dify.ai) or [self-hosted](https://docs.dify.ai/getting-started/install-self-hosted))
3. You have the base URL and API key for your deployed model

### Configuration Steps

1. Log in to your Dify dashboard
2. Navigate to the **Settings** section
3. Select **Model Providers**
4. Click on **Add** and select **Custom** or **OpenAI API Compatible**
5. Configure the provider with the following information:
   - **Provider Name**: A name for your EMD model provider (e.g., "EMD Models")
   - **Base URL**: The endpoint URL of your EMD-deployed model (e.g., `https://your-endpoint.execute-api.region.amazonaws.com`)
   - **API Key**: Your API key for accessing the model
   - **Available Models**: Add the model IDs of your deployed models
6. Click **Save** to add the provider

Once configured, your EMD-deployed models will appear in the model selection dropdown when creating applications in Dify.

## Example Use Cases

With your EMD models integrated into Dify, you can build various applications:

- **Conversational AI**: Create chatbots and virtual assistants using your custom models
- **Document Processing**: Build RAG applications that use your models to process and analyze documents
- **AI Workflows**: Design complex workflows that incorporate your models at different stages
- **Custom Agents**: Create AI agents that use your models for reasoning and decision-making
- **API Services**: Expose your models as APIs with additional processing logic

## Troubleshooting

If you encounter issues connecting to your EMD-deployed model:

1. Verify that your model is properly deployed and running
2. Check that the Base URL is correct and includes the full endpoint path
3. Ensure your API key has the necessary permissions
4. Confirm that your model ID exactly matches the deployed model's identifier
5. Test the connection using a simple API request before integrating with Dify

## Additional Resources

- [Dify GitHub Repository](https://github.com/langgenius/dify)
- [Dify Documentation](https://docs.dify.ai)
- [EMD Supported Models](supported_models.md)
