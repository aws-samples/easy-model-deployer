
# Test OpenAI compatible interface

### Sample Code
```python
import openai
# Change the api_key here to the parameter you passed in via extra-parameter
api_key = "your_openai_api_key"
def chat_with_openai_stream(prompt):
    client = openai.OpenAI(
        api_key=api_key,
        base_url="http://ec2-54-189-171-204.us-west-2.compute.amazonaws.com:8080/v1"
    )
    response = client.chat.completions.create(
        model="Qwen2.5-72B-Instruct-AWQ",
        # model="Qwen2.5-1.5B-Instruct",
        messages=[
        {"role": "user", "content": prompt}
        ],
        stream=True,
        temperature=0.6
    )
    print("AI: ", end="", flush=True)
    print(response)
    for chunk in response:
        content = chunk.choices[0].delta.content
        think = getattr(chunk.choices[0].delta,"reasoning_content",None)
        if think is not None:
            print(think,end="",flush=True)
        else:
            print(content, end="", flush=True)
    print("\n")

def chat_with_openai(prompt):
    client = openai.OpenAI(
        api_key=api_key,
        base_url="http://127.0.0.1:9000/v1"
    )
    response = client.chat.completions.create(
        model="DeepSeek-R1-Distill-Qwen-1.5B",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        stream=False
    )
    print(response)

# Test the stream and non-stream interface
chat_with_openai_stream("What is the capital of France?")
chat_with_openai("What is the capital of France?")
```
