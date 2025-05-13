# LangChain Integration

This guide covers how to integrate with deployed models using the LangChain framework.

## LLM Models

```python
from emd.integrations.langchain_clients import SageMakerVllmChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Initialize the chat model
chat_model = SageMakerVllmChatModel(
    model_id="Qwen2.5-7B-Instruct",
    model_kwargs={
        "temperature": 0.5,
    }
)

# Create a simple chain
chain = chat_model | StrOutputParser()

# Define messages
messages = [
    HumanMessage(content="What is the capital of France?"),
]

# Invoke the chain
response = chain.invoke(messages)
print(response)
```

## Function Calling with LangChain

```python
from langchain.tools.base import StructuredTool
from langchain_core.utils.function_calling import (
    convert_to_openai_function,
    convert_to_openai_tool
)

# Define a function
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get the current weather in a given location"""
    # This would call a weather API in a real application
    return f"The weather in {location} is sunny and 25 degrees {unit}"

# Create a tool
weather_tool = StructuredTool.from_function(get_weather)

# Convert to OpenAI tool format
openai_tool = convert_to_openai_tool(weather_tool)

# Initialize the model with tools
chat_model = SageMakerVllmChatModel(
    model_id="Qwen2.5-7B-Instruct",
    model_kwargs={
        "tools": [openai_tool],
        "tool_choice": "auto"
    }
)

# Invoke with a query that should trigger tool use
messages = [
    HumanMessage(content="What's the weather like in Paris?")
]

response = chat_model.invoke(messages)
print(response)
```

## Embedding Models

```python
import time
from emd.integrations.langchain_clients import SageMakerVllmEmbeddings

# Initialize the embedding model
embedding_model = SageMakerVllmEmbeddings(
    model_id="bge-m3",
)

# Get embeddings for a single text
text = 'The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.'
embedding = embedding_model.embed_query(text)

# Get embeddings for multiple documents
documents = [text] * 10  # 10 copies of the same text for demonstration
embeddings = embedding_model.embed_documents(documents)

print(f"Single embedding dimension: {len(embedding)}")
print(f"Number of document embeddings: {len(embeddings)}")
```

## Reranking Models

```python
from emd.integrations.langchain_clients import SageMakerVllmRerank

# Initialize the reranker
rerank_model = SageMakerVllmRerank(
    model_id="bge-reranker-v2-m3"
)

# Define documents and query
docs = [
    "The giant panda is a bear species endemic to China.",
    "Paris is the capital of France.",
    "Machine learning is a subset of artificial intelligence."
]
query = 'What is a panda?'

# Rerank documents based on relevance to the query
results = rerank_model.rerank(query=query, documents=docs)

# Print results
for result in results:
    print(f"Document: {result.document}")
    print(f"Score: {result.relevance_score}")
    print("---")
```

## Vision Models (VLM)

For vision models, you can use the EMD CLI to invoke them:

```bash
# Upload an image to S3
aws s3 cp image.jpg s3://your-bucket/image.jpg

# Invoke the vision model
emd invoke Qwen2-VL-7B-Instruct
```

When prompted:
- Enter the S3 path to your image: `s3://your-bucket/image.jpg`
- Enter your prompt: `What's in this image?`
