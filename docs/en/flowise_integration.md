# Flowise Integration

This guide covers how to integrate EMD-deployed models with [Flowise](https://github.com/FlowiseAI/Flowise), an open-source UI for building LLM applications.

## Overview

Flowise is a powerful drag-and-drop interface for building custom AI workflows. It provides a visual way to connect various components like language models, embeddings, vector stores, and more to create complex LLM applications without writing code. By integrating EMD-deployed models with Flowise, you can leverage your custom models in sophisticated AI workflows.

With Flowise, you can:
- Build LLM applications using a visual interface
- Connect your EMD-deployed models to various components
- Create chatbots, document Q&A systems, and other AI applications
- Deploy your workflows as API endpoints
- Share your workflows with others

## Key Features of Flowise

- **Visual Flow Builder**: Drag-and-drop interface for creating AI workflows
- **Component Library**: Pre-built components for various LLM operations
- **API Deployment**: Deploy your workflows as API endpoints
- **Chatbot Interface**: Built-in chatbot interface for testing
- **Custom Components**: Add your own custom components
- **Marketplace**: Share and discover workflows created by the community

## Integrating EMD Models with Flowise

EMD-deployed models can be integrated with Flowise through its OpenAI API compatibility. This allows you to use your custom models in various Flowise components that support OpenAI-compatible APIs.

### Prerequisites

1. You have successfully deployed a model using EMD with the OpenAI Compatible API enabled
2. You have installed and set up Flowise (either [locally](https://github.com/FlowiseAI/Flowise#installation) or using [Docker](https://github.com/FlowiseAI/Flowise#docker))
3. You have the base URL and API key for your deployed model

### Configuration Steps

1. Launch Flowise and log in to the interface
2. Create a new canvas or open an existing one
3. From the components panel, search for and add the "ChatOpenAI" component to your canvas
4. Configure the ChatOpenAI component with the following settings:
   - **Base URL**: The endpoint URL of your EMD-deployed model (e.g., `https://your-endpoint.execute-api.region.amazonaws.com`)
   - **API Key**: Your API key for accessing the model
   - **Model Name**: The ID of your deployed model
5. Connect the ChatOpenAI component to other components in your workflow
6. Test your workflow using the built-in chatbot interface

## Example Use Cases

With your EMD models integrated into Flowise, you can build various applications:

- **Conversational AI**: Create chatbots and virtual assistants using your custom models
- **Document Q&A**: Build systems that can answer questions based on document content
- **Knowledge Bases**: Create searchable knowledge bases with RAG (Retrieval-Augmented Generation)
- **Content Generation**: Generate content based on specific inputs and constraints
- **Data Analysis**: Extract insights from structured and unstructured data

## Troubleshooting

If you encounter issues connecting to your EMD-deployed model:

1. Verify that your model is properly deployed and running
2. Check that the Base URL is correct and includes the full endpoint path
3. Ensure your API key has the necessary permissions
4. Confirm that your model ID exactly matches the deployed model's identifier
5. Check the Flowise logs for any error messages

## Additional Resources

- [Flowise GitHub Repository](https://github.com/FlowiseAI/Flowise)
- [Flowise Documentation](https://docs.flowiseai.com)
- [EMD Supported Models](supported_models.md)
