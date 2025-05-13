# Ollama Integration

This guide covers how to integrate EMD-deployed models with [Ollama](https://github.com/ollama/ollama), an open-source framework for running large language models locally.

## Overview

Ollama is a popular tool that allows you to run large language models locally on your own hardware. It provides a simple way to download, run, and manage various open-source models. By integrating EMD-deployed models with Ollama, you can create a hybrid setup that leverages both local models and your custom cloud-deployed models.

With Ollama integration, you can:
- Use both local models and EMD-deployed models in your applications
- Create fallback mechanisms between local and cloud models
- Compare performance between local and cloud-deployed versions
- Develop applications that work both online and offline
- Optimize for cost, performance, or privacy based on specific needs

## Key Features of Ollama

- **Local Model Execution**: Run models on your own hardware
- **Simple API**: Easy-to-use REST API for model interaction
- **Model Library**: Access to various open-source models
- **Customization**: Create and customize model configurations
- **Cross-platform**: Available for macOS, Windows, and Linux
- **Low Resource Usage**: Optimized for running on consumer hardware

## Integrating EMD Models with Ollama

There are several ways to integrate EMD-deployed models with Ollama:

### 1. API Orchestration

You can build an orchestration layer that routes requests between Ollama's API and your EMD-deployed model's API based on specific criteria.

#### Prerequisites

1. You have successfully deployed a model using EMD with the OpenAI Compatible API enabled
2. You have [installed Ollama](https://github.com/ollama/ollama#installation) on your local machine
3. You have the base URL and API key for your deployed EMD model

#### Implementation Example

Here's a simple Python example that routes requests between Ollama and an EMD-deployed model:

```python
import requests
import json

def generate_text(prompt, use_local=True, max_tokens=100):
    """
    Generate text using either Ollama (local) or EMD-deployed model (cloud)

    Args:
        prompt (str): The input prompt
        use_local (bool): Whether to use local Ollama model
        max_tokens (int): Maximum tokens to generate

    Returns:
        str: Generated text
    """
    if use_local:
        # Use Ollama API (local)
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",  # or any other model you have pulled
                "prompt": prompt,
                "max_tokens": max_tokens
            }
        )
        return response.json().get("response", "")
    else:
        # Use EMD-deployed model API (cloud)
        response = requests.post(
            "https://your-endpoint.execute-api.region.amazonaws.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer your-api-key"
            },
            json={
                "model": "your-deployed-model-id",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens
            }
        )
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

# Example usage
result = generate_text("Explain quantum computing", use_local=True)
print(result)

result = generate_text("Explain quantum computing", use_local=False)
print(result)
```

### 2. Fallback Mechanism

You can implement a fallback mechanism that tries the local Ollama model first and falls back to the EMD-deployed model if the local model fails or produces unsatisfactory results.

```python
def generate_with_fallback(prompt, max_tokens=100):
    """
    Try local model first, fall back to cloud model if needed

    Args:
        prompt (str): The input prompt
        max_tokens (int): Maximum tokens to generate

    Returns:
        str: Generated text
    """
    try:
        # Try Ollama first
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "max_tokens": max_tokens
            },
            timeout=5  # Set a timeout for local model
        )

        if response.status_code == 200:
            result = response.json().get("response", "")
            if result and len(result) > 20:  # Simple quality check
                return {"source": "local", "text": result}
    except Exception as e:
        print(f"Local model error: {e}")

    # Fall back to EMD-deployed model
    try:
        response = requests.post(
            "https://your-endpoint.execute-api.region.amazonaws.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer your-api-key"
            },
            json={
                "model": "your-deployed-model-id",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens
            }
        )

        if response.status_code == 200:
            result = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"source": "cloud", "text": result}
    except Exception as e:
        print(f"Cloud model error: {e}")

    return {"source": "none", "text": "Failed to generate response from both local and cloud models."}
```

## Example Use Cases

With your EMD models integrated with Ollama, you can build various applications:

- **Hybrid AI Applications**: Applications that use local models for basic tasks and cloud models for more complex tasks
- **Offline-First Applications**: Applications that work offline with local models but enhance capabilities when online
- **Cost-Optimized Solutions**: Use local models for frequent, simple queries and cloud models for important or complex queries
- **Privacy-Focused Applications**: Process sensitive data locally and only use cloud models for non-sensitive data
- **Development and Testing**: Use local models during development and testing, and cloud models in production

## Troubleshooting

If you encounter issues with the integration:

1. Verify that Ollama is running locally (`ollama list` should show available models)
2. Check that your EMD model is properly deployed and accessible
3. Ensure API endpoints and authentication details are correct
4. Check network connectivity if using cloud models
5. Monitor resource usage if local models are running slowly

## Additional Resources

- [Ollama GitHub Repository](https://github.com/ollama/ollama)
- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [EMD Supported Models](supported_models.md)
