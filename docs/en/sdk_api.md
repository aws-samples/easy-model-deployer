# SDK API Documentation

> **Getting Started**: The EMD SDK provides a comprehensive Python interface for deploying, managing, and invoking machine learning models on AWS infrastructure. Install the SDK with `pip install easy-model-deployer` and import the modules you need.
>
> Quick example:
> ```python
> from emd.sdk import bootstrap, deploy, destroy
> from emd.sdk.clients.sagemaker_client import SageMakerClient
>
> # Bootstrap infrastructure
> bootstrap()
>
> # Deploy a model
> result = deploy(
>     model_id="Qwen2.5-7B-Instruct",
>     instance_type="ml.g5.xlarge",
>     engine_type="vllm",
>     service_type="sagemaker"
> )
>
> # Use the deployed model
> client = SageMakerClient(model_id="Qwen2.5-7B-Instruct")
> response = client.invoke({
>     "messages": [{"role": "user", "content": "Hello!"}]
> })
> ```

## Bootstrap Infrastructure

Initialize AWS resources required for model deployment.

**Function:** `bootstrap()`

**Python Example:**
```python
from emd.sdk.bootstrap import bootstrap

# Initialize AWS infrastructure
bootstrap()
```

**Advanced Example:**
```python
from emd.sdk.bootstrap import create_env_stack

# Create environment stack with custom parameters
create_env_stack(
    region="us-east-1",
    stack_name="my-emd-env-stack",
    bucket_name="my-emd-bucket",
    force_update=True
)
```

## Deploy Models

Deploy machine learning models to AWS services.

**Function:** `deploy(model_id, instance_type, engine_type, service_type, **kwargs)`

**Parameters:**

- `model_id` (required): Model identifier (e.g., "Qwen2.5-7B-Instruct", "DeepSeek-R1-Distill-Llama-8B")
- `instance_type` (required): AWS instance type (e.g., "ml.g5.xlarge", "g5.2xlarge")
- `engine_type` (required): Inference engine ("vllm", "tgi", "huggingface")
- `service_type` (required): AWS service ("sagemaker", "ecs", "ec2")
- `framework_type`: API framework (default: "fastapi")
- `model_tag`: Model version tag (default: "dev")
- `waiting_until_deploy_complete`: Wait for completion (default: True)
- `extra_params`: Additional deployment parameters

**Basic Example:**
```python
from emd.sdk.deploy import deploy

# Deploy a model to SageMaker
result = deploy(
    model_id="Qwen2.5-7B-Instruct",
    instance_type="ml.g5.xlarge",
    engine_type="vllm",
    service_type="sagemaker"
)

print(f"Deployment ID: {result['pipeline_execution_id']}")
print(f"Model Stack: {result['model_stack_name']}")
```

**Advanced Example:**
```python
from emd.sdk.deploy import deploy

# Deploy with custom parameters
result = deploy(
    model_id="DeepSeek-R1-Distill-Llama-8B",
    instance_type="ml.g5.2xlarge",
    engine_type="vllm",
    service_type="sagemaker",
    model_tag="production",
    extra_params={
        "engine_params": {
            "cli_args": "--max_model_len 16000 --max_num_seqs 4"
        },
        "service_params": {
            "api_key": "your-secure-api-key"
        }
    }
)
```

**Local Deployment Example:**
```python
from emd.sdk.deploy import deploy_local

# Deploy locally for testing
deploy_local(
    model_id="Qwen2.5-7B-Instruct",
    instance_type="cpu",
    service_type="local",
    engine_type="vllm",
    extra_params={"temperature": 0.7}
)
```

## Model Status

Check the deployment status of models.

**Function:** `get_model_status(model_id, model_tag)`

**Python Example:**
```python
from emd.sdk.status import get_model_status

# Check status of a specific model
status = get_model_status("Qwen2.5-7B-Instruct", "dev")

# Check in-progress deployments
for deployment in status["inprogress"]:
    print(f"Model: {deployment['model_id']}")
    print(f"Status: {deployment['status']}")
    print(f"Stage: {deployment.get('stage_name', 'N/A')}")

# Check completed deployments
for deployment in status["completed"]:
    print(f"Model: {deployment['model_id']}")
    print(f"Service: {deployment['service_type']}")
    print(f"Endpoint: {deployment.get('endpoint_name', 'N/A')}")
```

**Pipeline Status Example:**
```python
from emd.sdk.status import get_pipeline_execution_status

# Check specific pipeline execution
status = get_pipeline_execution_status(
    pipeline_execution_id="execution-123",
    region="us-east-1"
)

print(f"Status: {status['status']}")
print(f"Succeeded: {status['is_succeeded']}")
```

## SageMaker Client

Interact with models deployed on Amazon SageMaker.

**Initialization:**
```python
from emd.sdk.clients.sagemaker_client import SageMakerClient

# Initialize with model ID
client = SageMakerClient(
    model_id="Qwen2.5-7B-Instruct",
    model_tag="dev",
    region_name="us-east-1"
)

# Or initialize with endpoint name directly
client = SageMakerClient(
    endpoint_name="my-sagemaker-endpoint",
    region_name="us-east-1"
)
```

**Synchronous Invocation:**
```python
# Basic chat completion
response = client.invoke({
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ],
    "max_tokens": 200,
    "temperature": 0.7
})

print(response["choices"][0]["message"]["content"])
```

**Streaming Example:**
```python
# Stream response tokens
for chunk in client.invoke({
    "messages": [{"role": "user", "content": "Tell me a story"}],
    "stream": True,
    "max_tokens": 500
}):
    if chunk.get("choices") and chunk["choices"][0].get("delta", {}).get("content"):
        print(chunk["choices"][0]["delta"]["content"], end="")
```

**Asynchronous Invocation:**
```python
# For long-running tasks
async_response = client.invoke_async({
    "messages": [{"role": "user", "content": "Write a detailed analysis"}],
    "max_tokens": 2000
})

# Wait for result
result = async_response.get_result()
print(result)
```

## ECS Client

Interact with models deployed on Amazon ECS.

**Python Example:**
```python
from emd.sdk.clients import ECSClient

# Initialize client
client = ECSClient(
    model_id="Qwen2.5-7B-Instruct",
    model_tag="dev"
)

# Invoke model
response = client.invoke({
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100,
    "temperature": 0.8
})

print(response["choices"][0]["message"]["content"])
```

**Streaming Example:**
```python
# Stream response from ECS deployment
for chunk in client.invoke({
    "messages": [{"role": "user", "content": "Explain quantum physics"}],
    "stream": True
}):
    print(chunk, end="")
```

## Conversation Interface

High-level interface for conversational AI interactions.

**Python Example:**
```python
from emd.sdk.invoke import ConversationInvoker

# Initialize conversation
conversation = ConversationInvoker("Qwen2.5-7B-Instruct", "dev")

# Set system message
conversation.add_system_message("You are a helpful AI assistant.")

# Add user message and get response
conversation.add_user_message("What is artificial intelligence?")
response = conversation.invoke()
print(response)

# Continue conversation
conversation.add_assistant_message(response)
conversation.add_user_message("Can you give me examples?")
response = conversation.invoke()
print(response)
```

**Streaming Conversation:**
```python
# Stream conversation response
conversation.add_user_message("Tell me about the future of AI")
for chunk in conversation.invoke(stream=True):
    print(chunk, end="")
```

## Destroy Deployments

Remove deployed models and clean up resources.

**Function:** `destroy(model_id, model_tag, waiting_until_complete)`

**Python Example:**
```python
from emd.sdk.destroy import destroy

# Destroy a deployed model
destroy(
    model_id="Qwen2.5-7B-Instruct",
    model_tag="dev",
    waiting_until_complete=True
)
```

**Stop Pipeline Example:**
```python
from emd.sdk.destroy import stop_pipeline_execution

# Stop an active deployment pipeline
stop_pipeline_execution(
    model_id="Qwen2.5-7B-Instruct",
    model_tag="dev",
    waiting_until_complete=True
)
```

## Embedding Models

Work with text embedding models.

**Python Example:**
```python
from emd.sdk.clients.sagemaker_client import SageMakerClient

# Initialize embedding model client
client = SageMakerClient(
    model_id="bge-m3",
    model_tag="dev"
)

# Get embeddings for single text
response = client.invoke({
    "input": "Machine learning is transforming technology",
    "normalize": True
})

embedding = response["data"][0]["embedding"]
print(f"Embedding dimension: {len(embedding)}")

# Get embeddings for multiple texts
response = client.invoke({
    "input": [
        "First document text",
        "Second document text",
        "Third document text"
    ]
})

print(f"Generated {len(response['data'])} embeddings")
```

## Reranking Models

Rerank documents based on relevance to a query.

**Python Example:**
```python
from emd.sdk.clients.sagemaker_client import SageMakerClient

# Initialize reranking model client
client = SageMakerClient(
    model_id="bge-reranker-v2-m3",
    model_tag="dev"
)

# Rerank documents
response = client.invoke({
    "query": "What is machine learning?",
    "documents": [
        "Machine learning is a subset of artificial intelligence.",
        "Paris is the capital of France.",
        "Deep learning uses neural networks."
    ],
    "max_rerank": 3
})

# Print ranked results
for i, result in enumerate(response["data"]):
    print(f"Rank {i+1}: {result['document']}")
    print(f"Score: {result['relevance_score']:.4f}")
    print("---")
```

## Vision Models

Process images with vision-language models.

**Python Example:**
```python
from emd.sdk.clients.sagemaker_client import SageMakerClient
import base64

# Function to encode image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Initialize vision model client
client = SageMakerClient(
    model_id="Qwen2-VL-7B-Instruct",
    model_tag="dev"
)

# Process image with text
base64_image = encode_image("path/to/image.jpg")
response = client.invoke({
    "messages": [
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
})

print(response["choices"][0]["message"]["content"])
```

## AWS Lambda Integration

Use the SDK in AWS Lambda functions.

**Lambda Function Example:**
```python
import json
from emd.sdk.clients.sagemaker_client import SageMakerClient

def lambda_handler(event, context):
    # Initialize client
    client = SageMakerClient(
        model_id=event['model_id'],
        region_name=context.invoked_function_arn.split(':')[3]
    )

    # Invoke model
    response = client.invoke({
        "messages": event['messages'],
        "max_tokens": event.get('max_tokens', 100)
    })

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
```

**Model Management Lambda:**
```python
import json
from emd.sdk import deploy, destroy, get_model_status

def lambda_handler(event, context):
    action = event['action']
    model_id = event['model_id']

    if action == 'deploy':
        result = deploy(
            model_id=model_id,
            instance_type=event['instance_type'],
            engine_type=event['engine_type'],
            service_type=event['service_type'],
            waiting_until_deploy_complete=False
        )
        return {'statusCode': 200, 'body': json.dumps(result)}

    elif action == 'destroy':
        destroy(model_id, waiting_until_complete=False)
        return {'statusCode': 200, 'body': json.dumps({'status': 'initiated'})}

    elif action == 'status':
        status = get_model_status(model_id)
        return {'statusCode': 200, 'body': json.dumps(status)}
```

## Error Handling

Handle common errors when using the SDK.

**Python Example:**
```python
from emd.sdk import deploy
from emd.sdk.clients.sagemaker_client import SageMakerClient
from botocore.exceptions import ClientError

try:
    # Deploy model
    result = deploy(
        model_id="Qwen2.5-7B-Instruct",
        instance_type="ml.g5.xlarge",
        engine_type="vllm",
        service_type="sagemaker"
    )

    # Initialize client
    client = SageMakerClient(model_id="Qwen2.5-7B-Instruct")

    # Invoke model
    response = client.invoke({
        "messages": [{"role": "user", "content": "Hello"}]
    })

except RuntimeError as e:
    print(f"Deployment error: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
except ClientError as e:
    print(f"AWS error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Complete Workflow Example

End-to-end example of deploying and using a model.

**Python Example:**
```python
from emd.sdk import bootstrap, deploy, get_model_status, destroy
from emd.sdk.clients.sagemaker_client import SageMakerClient
import time

# 1. Bootstrap infrastructure
print("Setting up AWS infrastructure...")
bootstrap()

# 2. Deploy model
print("Deploying model...")
deployment = deploy(
    model_id="Qwen2.5-7B-Instruct",
    instance_type="ml.g5.xlarge",
    engine_type="vllm",
    service_type="sagemaker",
    extra_params={
        "engine_params": {
            "cli_args": "--max_model_len 8000 --max_num_seqs 10"
        }
    }
)

print(f"Deployment started: {deployment['pipeline_execution_id']}")

# 3. Wait for deployment to complete
print("Waiting for deployment...")
while True:
    status = get_model_status("Qwen2.5-7B-Instruct")
    if status["completed"]:
        print("Deployment completed!")
        break
    elif status["inprogress"]:
        print("Still deploying...")
        time.sleep(30)
    else:
        print("No deployment found")
        break

# 4. Use the deployed model
client = SageMakerClient(model_id="Qwen2.5-7B-Instruct")

# Test basic functionality
response = client.invoke({
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain machine learning in simple terms."}
    ],
    "max_tokens": 200,
    "temperature": 0.7
})

print("Model response:")
print(response["choices"][0]["message"]["content"])

# Test streaming
print("\nStreaming response:")
for chunk in client.invoke({
    "messages": [{"role": "user", "content": "Count from 1 to 10"}],
    "stream": True
}):
    if chunk.get("choices") and chunk["choices"][0].get("delta", {}).get("content"):
        print(chunk["choices"][0]["delta"]["content"], end="")

# 5. Clean up (optional)
# destroy("Qwen2.5-7B-Instruct")
