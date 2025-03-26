# embedding
# import requests

# texts = [
#     "apple",
#     "strawberry"
# ]

# # url = "http://ec2-34-219-216-209.us-west-2.compute.amazonaws.com:8080/invocations"
# url = "http://0.0.0.0:8080/invocations"
# r = requests.post(url,json={"input":texts})
# print(r.json())

# rerank
import requests

query = "apple"

documents = [
    # "apple",
    "strawberry"
]

# url = "http://ec2-34-219-216-209.us-west-2.compute.amazonaws.com:8080/invocations"
url = "http://0.0.0.0:8080/invocations"
r = requests.post(url,json={"query":query,"documents":documents})
print(r.json())

# llm
# import requests

# messages = [
#     {
#         "role": "system",
#         "content": "You are a helpful and harmless assistant. You are Qwen developed by Alibaba. You should think step-by-step.",
#     },
#     {
#         "role": "user",
#         "content": "How many r in strawberry.",
#     },
# ]

# # url = "http://ec2-34-219-216-209.us-west-2.compute.amazonaws.com:8080/invocations"
# url = "http://0.0.0.0:9000/invocations"
# r = requests.post(url,json={"messages":messages})
# print(r.text)



# import requests

# def stream_request(url, params=None, headers=None):
#     """
#     发送流式请求并逐行打印响应
#     :param url: 请求的 URL
#     :param params: 可选的 URL 参数
#     :param headers: 可选的请求头
#     """
#     with requests.post(url, json=params, headers=headers, stream=True) as response:
#         # 检查响应状态码
#         response.raise_for_status()

#         # 逐行读取流式数据
#         for line in response.iter_lines():
#             if line:
#                 print(line.decode('utf-8'))  # 解码并打印每一行数据

# # 示例调用（这里使用一个测试 API，替换成你的流式 API）
# url = "http://127.0.0.1:9000/v1/chat/completions"
# headers = {"Accept": "text/event-stream"}

# params = {
#   "model": "DeepSeek-R1-Distill-Qwen-1.5B",
#   "messages": [
#     {
#       "role": "user",
#       "content": "hi"
#     }
#   ],
#   "stream":True
# }
# stream_request(url, headers=headers,params=params)
