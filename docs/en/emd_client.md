
# Usse EMD client to invoke deployed models

```bash
emd invoke MODEL_ID MODEL_TAG (Optional)
```

## LLM models
```python
from emd.integrations.langchain_clients import SageMakerVllmChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
from langchain.tools.base import StructuredTool
from langchain_core.utils.function_calling import (
    convert_to_openai_function,
    convert_to_openai_tool
)
chat_model = SageMakerVllmChatModel(
    model_id="Qwen2.5-7B-Instruct",
    model_kwargs={
        "temperature":0.5,
    }
)
chain = chat_model | StrOutputParser()
messages = [
        HumanMessage(content="9.11和9.9两个数字哪个更大？"),
    ]
print(chain.invoke(messages))
```

## VLM models
1. upload image to a s3 path
![alt text](../images/sample.png)
```bash
aws s3 cp image.jpg s3://your-bucket/image.jpg
```

2. invoke the model
```bash
emd invoke  Qwen2-VL-7B-Instruct
...
Invoking model Qwen2-VL-7B-Instruct with tag dev
Enter image path(local or s3 file): s3://your-bucket/image.jpg
Enter prompt: What's in this image?
...
```

### Video(Txt2edding) models
1. input prompt for video generation
```bash
emd invoke txt2video-LTX
...
Invoking model txt2video-LTX with tag dev
Write a prompt, press Enter to generate a response (Ctrl+C to abort),
User: Two police officers in dark blue uniforms and matching hats enter a dimly lit room through a doorway on the left side of the frame. The first officer, with short brown hair and a mustache, steps inside first, followed by his partner, who has a shaved head and a goatee. Both officers have serious expressions and maintain a steady pace as they move deeper into the room. The camera remains stationary, capturing them from a slightly low angle as they enter. The room has exposed brick walls and a corrugated metal ceiling, with a barred window visible in the background. The lighting is low-key, casting shadows on the officers' faces and emphasizing the grim atmosphere. The scene appears to be from a film or television show.
...
```
2. download generated video from **output_path**

##  Embedding models
```python
import time
from emd.integrations.langchain_clients import SageMakerVllmEmbeddings
from emd.integrations.langchain_clients import SageMakerVllmRerank
embedding_model = SageMakerVllmEmbeddings(
    model_id="bge-m3",
)
text = 'The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.'
t0 = time.time()
r1 = embedding_model.embed_query(text)
t1 = time.time()
embedding_model.embed_documents([text]*1000)
t2 = time.time()
print(f"embed_query: {t1-t0}")
print(f"embed_documents: {t2-t1}")
```

##  Rerank models
```python
import time
from emd.integrations.langchain_clients import SageMakerVllmEmbeddings
from emd.integrations.langchain_clients import SageMakerVllmRerank
embedding_model = SageMakerVllmEmbeddings(
    model_id="bge-m3",
    # model_tag='dev-2'
)
text = 'The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.'
t0 = time.time()
r1 = embedding_model.embed_query(text)
t1 = time.time()
embedding_model.embed_documents([text]*1000)
t2 = time.time()
print(f"embed_query: {t1-t0}")
print(f"embed_documents: {t2-t1}")
# docs = ["hi",'The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.']
# query = 'what is panda?'
# rerank_model = SageMakerVllmRerank(
#     model_id="bge-reranker-v2-m3"
# )
# print(rerank_model.rerank(query=query,documents=docs))
```
