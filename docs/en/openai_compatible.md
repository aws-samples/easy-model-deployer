# OpenAI Compatible API

EMD provides an OpenAI-compatible API interface for all deployed models, making it easy to integrate with existing tools and libraries that support the OpenAI API format.

## Overview

The OpenAI-compatible API allows you to:

- Use the familiar OpenAI API format for interacting with your deployed models
- Integrate with existing tools and libraries that support OpenAI's API
- Switch between OpenAI's services and your deployed models with minimal code changes
- Access advanced features like streaming responses and function calling

## Getting Started

To use the OpenAI-compatible API with your deployed models:

1. Deploy a model using EMD
2. Retrieve the base URL and API key using `emd status`
3. Use the OpenAI client library or direct API calls to interact with your model

## API Endpoints

EMD's OpenAI-compatible API supports the following endpoints:

- `/v1/models` - List available models
- `/v1/chat/completions` - Create chat completions
- `/v1/embeddings` - Generate embeddings
- `/v1/rerank` - Rerank documents
- `/v1/invocations` - General-purpose model invocations
- `/v1/audio/transcriptions` - Transcribe audio (for supported models)

## Authentication

All API requests require authentication using an API key. Include the API key in the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

## Examples

### Chat Completions

```python
import openai

client = openai.OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://YOUR_EMD_ENDPOINT/v1"
)

# Create a chat completion
response = client.chat.completions.create(
    model="YOUR_MODEL_ID/dev",  # Model ID with tag
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,
    stream=False
)

# Print the response
print(response.choices[0].message.content)
```

### Streaming Example

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://YOUR_EMD_ENDPOINT/v1"
)

# Create a streaming chat completion
stream = client.chat.completions.create(
    model="YOUR_MODEL_ID/dev",  # Model ID with tag
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short poem about AI."}
    ],
    stream=True
)

# Process the stream
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
print()
```

### Embeddings

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://YOUR_EMD_ENDPOINT/v1"
)

# Get embeddings for a single text
response = client.embeddings.create(
    model="YOUR_EMBEDDING_MODEL_ID/dev",  # Embedding model ID with tag
    input="The food was delicious and the service was excellent."
)

# Print the embedding vector
print(response.data[0].embedding)
```

## Supported Features

Depending on the model and deployment configuration, the following features are supported:

- **Streaming responses**: Real-time token generation
- **Function calling**: For models that support it
- **Vision capabilities**: For multimodal models
- **Custom parameters**: Temperature, top_p, max_tokens, etc.

## Limitations

- Some advanced OpenAI API features may not be available depending on the model
- Performance characteristics may differ from OpenAI's models
- API response formats match OpenAI's but may include additional fields specific to EMD

## Additional Resources

For more detailed information, see:

- [API Documentation](api.md)
- [Supported Models](supported_models.md)
- [Integration Examples](sdk_integration.md)
