import requests

messages = [
    {
        "role": "system",
        "content": "You are a helpful and harmless assistant. You are Qwen developed by Alibaba. You should think step-by-step.",
    },
    {
        "role": "user",
        "content": "How many r in strawberry.",
    },
]

# url = "http://ec2-34-219-216-209.us-west-2.compute.amazonaws.com:8080/invocations"
url = "http://0.0.0.0:8080/invocations"
r = requests.post(url,json={"messages":messages})
print(r.text)