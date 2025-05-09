# NextChat Integration

This guide covers how to integrate EMD-deployed models with [NextChat](https://github.com/ChatGPTNextWeb/ChatGPT-Next-Web), an open-source cross-platform ChatGPT web UI.

## Overview

NextChat (ChatGPT-Next-Web) is a popular open-source project that provides a clean, intuitive web interface for interacting with various large language models. It supports multiple models including OpenAI's GPT models, and importantly, any OpenAI API-compatible endpoints. By integrating EMD-deployed models with NextChat, you can create a user-friendly interface for interacting with your custom models.

With NextChat, you can:
- Access your EMD-deployed models through a polished web interface
- Create and manage multiple conversations
- Save and share conversation history
- Customize the UI to match your preferences
- Deploy the interface on various platforms

## Key Features of NextChat

- **Clean User Interface**: Modern, responsive design for desktop and mobile
- **Multi-model Support**: Switch between different models easily
- **Conversation Management**: Create, save, and organize conversations
- **Prompt Templates**: Create and use templates for common prompts
- **Markdown Support**: Rich text formatting with Markdown
- **Self-hosting**: Deploy on your own infrastructure
- **Cross-platform**: Available as a web app, PWA, or desktop application

## Integrating EMD Models with NextChat

EMD-deployed models can be easily integrated with NextChat through its OpenAI API compatibility. This allows you to use your custom models with all the features and convenience of the NextChat interface.

### Prerequisites

1. You have successfully deployed a model using EMD with the OpenAI Compatible API enabled
2. You have access to NextChat (either through the [hosted version](https://chat.nextchat.dev) or by [self-hosting](https://github.com/ChatGPTNextWeb/ChatGPT-Next-Web#environment-variables))
3. You have the base URL and API key for your deployed model

### Configuration Steps

1. Access NextChat through your browser
2. Click on the settings icon in the sidebar
3. Navigate to the "Models" section
4. Click "Add Custom Model"
5. Configure your EMD-deployed model with the following settings:
   - **Name**: A name for your model (e.g., "My EMD Model")
   - **Base URL**: The endpoint URL of your EMD-deployed model (e.g., `https://your-endpoint.execute-api.region.amazonaws.com`)
   - **API Key**: Your API key for accessing the model
   - **Model Name**: The ID of your deployed model
6. Save the configuration
7. Select your custom model from the model dropdown in the chat interface

### Self-hosting NextChat with EMD Integration

If you prefer to self-host NextChat, you can configure it to use your EMD-deployed model by default:

1. Clone the NextChat repository:
   ```bash
   git clone https://github.com/ChatGPTNextWeb/ChatGPT-Next-Web.git
   cd ChatGPT-Next-Web
   ```

2. Create a `.env.local` file with the following environment variables:
   ```
   OPENAI_API_KEY=your-api-key
   BASE_URL=https://your-endpoint.execute-api.region.amazonaws.com
   NEXT_PUBLIC_DEFAULT_MODEL=your-deployed-model-id
   ```

3. Build and run the application:
   ```bash
   npm install
   npm run build
   npm run start
   ```

## Example Use Cases

With your EMD models integrated into NextChat, you can:

- **Personal Assistant**: Create a personalized AI assistant using your custom-trained model
- **Customer Support**: Deploy a customer support interface with domain-specific knowledge
- **Content Creation**: Use the interface for brainstorming and content generation
- **Educational Tool**: Create an educational interface with specialized knowledge
- **Research Assistant**: Build a research assistant with access to specific research domains

## Troubleshooting

If you encounter issues connecting to your EMD-deployed model:

1. Verify that your model is properly deployed and running
2. Check that the Base URL is correct and includes the full endpoint path
3. Ensure your API key has the necessary permissions
4. Confirm that your model ID exactly matches the deployed model's identifier
5. Check browser console logs for any error messages

## Additional Resources

- [NextChat GitHub Repository](https://github.com/ChatGPTNextWeb/ChatGPT-Next-Web)
- [NextChat Documentation](https://docs.nextchat.dev)
- [EMD Supported Models](supported_models.md)
