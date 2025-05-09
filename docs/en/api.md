# API Documentation

> **Getting Started**: To obtain the base URL and API key for your deployed models, run `emd status` in your terminal. The command will display a table with your deployed models and their details, including a link to retrieve the API key from AWS Secrets Manager. The base URL is shown at the bottom of the output.
>
> Example output:
> ```
> Models
> ┌────────────────────────┬───────────────────────────────────────────────────────────────────────┐
> │ Model ID               │ Qwen2.5-0.5B-Instruct/dev                                             │
> │ Status                 │ CREATE_COMPLETE                                                       │
> │ Service Type           │ Amazon SageMaker AI Real-time inference with OpenAI Compatible API    │
> │ Instance Type          │ ml.g5.2xlarge                                                         │
> │ Create Time            │ 2025-05-08 12:27:05 UTC                                               │
> │ Query Model API Key    │ https://console.aws.amazon.com/secretsmanager/secret?name=EMD-APIKey- │
> │                        │ Secrets&region=us-east-1                                              │
> │ SageMakerEndpointName  │ EMD-Model-qwen2-5-0-5b-instruct-endpoint                              │
> └────────────────────────┴───────────────────────────────────────────────────────────────────────┘
>
> Base URL
> http://your-emd-endpoint.region.elb.amazonaws.com/v1
> ```

## List Models

Returns a list of available models.

**Endpoint:** `GET /v1/models`

**Curl Example:**
```bash
curl https://BASE_URL/v1/models
```

**Python Example:**
```python
from openai import OpenAI

client = OpenAI(
    # No API key needed for listing models
    base_url="https://BASE_URL"
)

# List available models
models = client.models.list()
for model in models.data:
    print(model.id)
```

## Chat Completions

Create a model response for a conversation.

**Endpoint:** `POST /v1/chat/completions`

**Parameters:**

- `model` (required): ID of the model to use (e.g., "Qwen2.5-7B-Instruct/dev", "Llama-3.3-70B-Instruct/dev")
- `messages` (required): Array of message objects with `role` and `content`
- `temperature`: Sampling temperature (0-2, default: 1)
- `top_p`: Nucleus sampling parameter (0-1, default: 1)
- `n`: Number of chat completion choices to generate (default: 1)
- `stream`: Whether to stream partial progress (default: false)
- `stop`: Sequences where the API will stop generating
- `max_tokens`: Maximum number of tokens to generate
- `presence_penalty`: Penalty for new tokens based on presence (-2.0 to 2.0)
- `frequency_penalty`: Penalty for new tokens based on frequency (-2.0 to 2.0)
- `function_call`: Controls how the model responds to function calls
- `functions`: List of functions the model may generate JSON inputs for

**Curl Example:**
```bash
curl https://BASE_URL/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen2.5-7B-Instruct/dev",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7
  }'
```

**Python Example:**
```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://BASE_URL"
)

# Create a chat completion
response = client.chat.completions.create(
    model="Qwen2.5-7B-Instruct/dev",  # Model ID with tag
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

**Streaming Example:**
```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://BASE_URL"
)

# Create a streaming chat completion
stream = client.chat.completions.create(
    model="Llama-3.3-70B-Instruct/dev",  # Model ID with tag
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

## Embeddings

Get vector representations of text.

**Endpoint:** `POST /v1/embeddings`

**Parameters:**

- `model` (required): ID of the model to use (e.g., "bge-m3/dev")
- `input` (required): Input text to embed or array of texts
- `user`: A unique identifier for the end-user

**Curl Example:**
```bash
curl https://BASE_URL/v1/embeddings \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bge-m3/dev",
    "input": "The food was delicious and the waiter..."
  }'
```

**Python Example:**
```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://BASE_URL"
)

# Get embeddings for a single text
response = client.embeddings.create(
    model="bge-m3/dev",  # Embedding model ID with tag
    input="The food was delicious and the service was excellent."
)

# Print the embedding vector
print(response.data[0].embedding)

# Get embeddings for multiple texts
response = client.embeddings.create(
    model="bge-m3/dev",  # Embedding model ID with tag
    input=[
        "The food was delicious and the service was excellent.",
        "The restaurant was very expensive and the food was mediocre."
    ]
)

# Print the number of embeddings
print(f"Generated {len(response.data)} embeddings")
```

## Rerank

Rerank a list of documents based on their relevance to a query.

**Endpoint:** `POST /v1/rerank`

**Parameters:**

- `model` (required): ID of the model to use (e.g., "bge-reranker-v2-m3/dev")
- `query` (required): The search query
- `documents` (required): List of documents to rerank
- `max_rerank`: Maximum number of documents to rerank (default: all)
- `return_metadata`: Whether to return metadata (default: false)

**Curl Example:**
```bash
curl https://BASE_URL/v1/rerank \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bge-reranker-v2-m3/dev",
    "query": "What is the capital of France?",
    "documents": [
      "Paris is the capital of France.",
      "Berlin is the capital of Germany.",
      "London is the capital of England."
    ]
  }'
```

**Python Example:**
```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://BASE_URL"
)

# Rerank documents based on a query
response = client.reranking.create(
    model="bge-reranker-v2-m3/dev",  # Reranking model ID with tag
    query="What is the capital of France?",
    documents=[
        "Paris is the capital of France.",
        "Berlin is the capital of Germany.",
        "London is the capital of England."
    ],
    max_rerank=3
)

# Print the reranked documents
for result in response.data:
    print(f"Document: {result.document}")
    print(f"Relevance Score: {result.relevance_score}")
    print("---")
```

## Invocations

General-purpose endpoint for model invocations.

**Endpoint:** `POST /v1/invocations`

**Parameters:**

- `model` (required): ID of the model to use
- `input`: Input data for the model
- `parameters`: Additional parameters for the model

**Curl Example:**
```bash
curl https://BASE_URL/v1/invocations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen2.5-7B-Instruct/dev",
    "input": {
      "query": "What is machine learning?"
    },
    "parameters": {
      "max_tokens": 100
    }
  }'
```

**Python Example:**
```python
import requests
import json

# Set up the API endpoint and headers
url = "https://BASE_URL/v1/invocations"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}

# Prepare the payload
payload = {
    "model": "Qwen2.5-7B-Instruct/dev",  # Model ID with tag
    "input": {
        "query": "What is machine learning?"
    },
    "parameters": {
        "max_tokens": 100
    }
}

# Make the API call
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Print the response
print(response.json())
```

## Vision Models

Process images along with text prompts.

**Endpoint:** `POST /v1/chat/completions`

**Parameters:**
Same as Chat Completions, but with messages that include image content.

**Python Example:**
```python
from openai import OpenAI
import base64

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "path/to/your/image.jpg"
base64_image = encode_image(image_path)

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://BASE_URL"
)

response = client.chat.completions.create(
    model="Qwen2-VL-7B-Instruct/dev",  # Vision model ID with tag
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)
```

## Audio Transcription

Transcribe audio files to text.

**Endpoint:** `POST /v1/audio/transcriptions`

**Python Example:**
```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://BASE_URL"
)

audio_file_path = "path/to/audio.mp3"
with open(audio_file_path, "rb") as audio_file:
    response = client.audio.transcriptions.create(
        model="whisper-large-v3/dev",  # ASR model ID with tag
        file=audio_file
    )

print(response.text)  # Transcribed text
```
