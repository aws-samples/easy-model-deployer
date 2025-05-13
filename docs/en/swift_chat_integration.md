# SwiftChat Integration

This guide covers how to integrate EMD-deployed models with [SwiftChat](https://github.com/aws-samples/swift-chat), a fast and responsive cross-platform AI chat application.

## Overview

SwiftChat is a cross-platform AI chat application developed with React Native that supports multiple model providers, including OpenAI Compatible models. This makes it an excellent client for interacting with models deployed using Easy Model Deployer (EMD).

With SwiftChat, you can:
- Chat with your EMD-deployed models in real-time with streaming responses
- Use rich markdown features including tables, code blocks, and LaTeX
- Access your models across Android, iOS, and macOS platforms
- Enjoy a fast, responsive, and privacy-focused experience

## Key Features of SwiftChat

- Real-time streaming chat with AI
- Rich Markdown support (tables, code blocks, LaTeX, etc.)
- AI image generation with progress indicators
- Multimodal support (images, videos & documents)
- Conversation history management
- Cross-platform support (Android, iOS, macOS)
- Tablet-optimized for iPad and Android tablets
- Multiple AI model providers supported
- Fully customizable system prompts

## Integrating EMD Models with SwiftChat

EMD-deployed models can be easily integrated with SwiftChat through its OpenAI Compatible interface. This allows you to use your own deployed models with all the features and convenience of the SwiftChat application.

### Prerequisites

1. You have successfully deployed a model using EMD with the OpenAI Compatible API enabled
2. You have installed SwiftChat on your device (Android, iOS, or macOS)
3. You have the base URL and API key for your deployed model

### Configuration Steps

1. Open SwiftChat on your device
2. Navigate to the Settings page
3. Select the OpenAI tab
4. Under OpenAI Compatible, enter the following information:
   - **Base URL**: The endpoint URL of your EMD-deployed model (e.g., `https://your-endpoint.execute-api.region.amazonaws.com`)
   - **API Key**: Your API key for accessing the model
   - **Model ID**: The ID of your deployed model(s), separate multiple models with commas
5. Select one of your models from the Text Model dropdown list

![SwiftChat OpenAI Compatible Settings](../images/sample.png)

## Example Use Cases

Once configured, you can use your EMD-deployed models in SwiftChat for various use cases:

- **Text Generation**: Chat with your models using the real-time streaming interface
- **Code Generation**: Ask your models to write or explain code, with proper syntax highlighting
- **Document Analysis**: Upload documents for your models to analyze (if multimodal models are supported)
- **Image Understanding**: Share images with vision-enabled models for analysis and discussion

## Troubleshooting

If you encounter issues connecting to your EMD-deployed model:

1. Verify that your model is properly deployed and running
2. Check that the Base URL is correct and includes the full endpoint path
3. Ensure your API key has the necessary permissions
4. Confirm that your model ID exactly matches the deployed model's identifier
5. Check network connectivity between your device and the model endpoint

## Additional Resources

- [SwiftChat GitHub Repository](https://github.com/aws-samples/swift-chat)
- [EMD Supported Models](supported_models.md)
