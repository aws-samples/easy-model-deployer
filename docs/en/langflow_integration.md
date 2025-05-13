# LangFlow Integration

This guide covers how to integrate EMD-deployed models with [LangFlow](https://github.com/langflow-ai/langflow), an open-source UI for LangChain.

## Overview

LangFlow is a user-friendly interface that allows you to build LangChain applications using a drag-and-drop visual editor. It provides a way to prototype and experiment with various LangChain components, including language models, without writing code. By integrating EMD-deployed models with LangFlow, you can easily incorporate your custom models into complex LangChain workflows.

With LangFlow, you can:
- Create complex LangChain flows using a visual interface
- Connect your EMD-deployed models to various components
- Prototype and test different configurations
- Export your flows as Python code
- Share your flows with others

## Key Features of LangFlow

- **Visual Flow Builder**: Drag-and-drop interface for creating LangChain flows
- **Component Library**: Pre-built components for various LangChain modules
- **Real-time Testing**: Test your flows directly in the interface
- **Code Export**: Export your flows as Python code
- **Custom Components**: Add your own custom components
- **Flow Sharing**: Share your flows with others

## Integrating EMD Models with LangFlow

EMD-deployed models can be integrated with LangFlow through its OpenAI API compatibility. This allows you to use your custom models in various LangChain components that support OpenAI-compatible APIs.

### Prerequisites

1. You have successfully deployed a model using EMD with the OpenAI Compatible API enabled
2. You have installed and set up LangFlow (either [locally](https://github.com/langflow-ai/langflow#installation) or using [Docker](https://github.com/langflow-ai/langflow#docker))
3. You have the base URL and API key for your deployed model

### Configuration Steps

1. Launch LangFlow and log in to the interface
2. Create a new flow or open an existing one
3. Add an LLM component to your flow (such as ChatOpenAI or OpenAI)
4. Configure the LLM component with the following settings:
   - **Base URL**: The endpoint URL of your EMD-deployed model (e.g., `https://your-endpoint.execute-api.region.amazonaws.com`)
   - **API Key**: Your API key for accessing the model
   - **Model Name**: The ID of your deployed model
5. Connect the LLM component to other components in your flow
6. Test your flow using the "Build" button

## Example Use Cases

With your EMD models integrated into LangFlow, you can build various applications:

- **Conversational Agents**: Create chatbots and virtual assistants using your custom models
- **Document Processing**: Build document processing pipelines with RAG (Retrieval-Augmented Generation)
- **Knowledge Extraction**: Extract structured information from unstructured text
- **Content Generation**: Generate content based on specific inputs and constraints
- **Multi-step Reasoning**: Create flows that break down complex problems into smaller steps

## Troubleshooting

If you encounter issues connecting to your EMD-deployed model:

1. Verify that your model is properly deployed and running
2. Check that the Base URL is correct and includes the full endpoint path
3. Ensure your API key has the necessary permissions
4. Confirm that your model ID exactly matches the deployed model's identifier
5. Check the LangFlow logs for any error messages

## Additional Resources

- [LangFlow GitHub Repository](https://github.com/langflow-ai/langflow)
- [LangFlow Documentation](https://docs.langflow.org)
- [EMD Supported Models](supported_models.md)
