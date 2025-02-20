from emd.sdk.clients.sagemaker_client import SageMakerClient


client = SageMakerClient(
    # model_id="Qwen2.5-72B-Instruct-AWQ"
    # model_id="internlm2_5-20b-chat-4bit-awq"
    model_id="deepseek-r1-distill-llama-70b-awq"
)

ret = client.invoke_async(
    {
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": "9.11和9.9哪个更大？"}]

            }
        ],
        "max_tokens": 512,
        "temperature": 0.6,
        "stream":False
    }
)
# for i in ret:
#     print(i['choices'][0]['delta']['content'],end="")
print(ret)


# client = SageMakerClient(
#     # model_id="Qwen2.5-72B-Instruct-AWQ"
#     model_id="internlm2_5-20b-chat-4bit-awq"
# )

# ret = client.invoke(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": [{"type": "text", "text": "9.11和9.9哪个更大？"}]

#             }
#         ],
#         "max_tokens": 512,
#         "temperature": 0.1,
#         "stream":True
#     }
# )
# for i in ret:
#     print(i['choices'][0]['delta']['content'],end="")



# client = SageMakerClient(
#     model_id="Qwen2.5-72B-Instruct-AWQ",
#     model_tag="Admin"
# )

# agent_pyload = {
#     'tools': [
#         {'type': 'function',
#           'function': {
#               'name': 'admin_qd_default',
#               'description': 'Answer question based on search result',
#               'parameters': {
#                   'properties': {},
#                   'type': 'object'
#             }}
#         },
#         {'type': 'function',
#          'function': {
#              'name': 'give_rhetorical_question',
#              'description': 'This tool is designed to handle the scenario when required parameters are missing from other tools. It prompts the user to provide the necessary information, ensuring that all essential parameters are collected before proceeding. This tools enhances user interaction by clarifying what is needed and improving the overall usability of the application.',
#              'parameters': {
#                  'properties': {
#                      'question': {
#                          'description': 'The rhetorical question to user. Example:\nInput: 今天天气怎么样?\nOutput: 请问您想了解哪个城市的天气?', 'type': 'string'
#                          }
#                     },
#                     'required': ['question'], 'type': 'object'
#                 }
#             }
#         },
#         {'type': 'function',
#          'function': {
#              'name': 'get_weather',
#              'description': 'Get the current weather for `city_name`',
#              'parameters': {
#                  'properties': {
#                      'city_name': {
#                          'description': "The name of the city. If the city name does not appear visibly in the user's response, please call the `give_rhetorical_question` to ask for city name.",
#                          'type': 'string'
#                         }
#                 },
#                 'required': ['city_name'],
#                 'type': 'object'
#             }
#         }
#         },
#         {'type': 'function',
#          'function': {
#              'name': 'give_final_response',
#              'description': 'If none of the other tools need to be called, call the current tool to complete the direct response to the user.',
#              'parameters': {
#                  'properties': {
#                      'response': {
#                          'description': 'Response to user', 'type': 'string'
#                     }
#             },
#             'required': ['response'], 'type': 'object'
#             }
#             }
#         }],
#         'messages': [
#             # {'role': 'system',
#             #  'content': "You are a helpful and honest AI assistant. Today is 2024年12月20日,星期五. \nHere are some guidelines for you:\n<guidelines>\n- Here are steps for you to decide to use which tool:\n    1. Determine whether the current context is sufficient to answer the user's question.\n    2. If the current context is sufficient to answer the user's question, call the `give_final_response` tool.\n    3. If the current context is not sufficient to answer the user's question, you can consider calling one of the provided tools.\n    4. If any of required parameters of the tool you want to call do not appears in context, call the `give_rhetorical_question` tool to ask the user for more information. \n- Always output with the same language as the content from user. If the content is English, use English to output. If the content is Chinese, use Chinese to output.\n- Always call one tool at a time.\n</guidelines>\nHere's some context for reference:\n<context>\n|问题|参考回复|\n|-|-|\n|出现疑难杂症？无法具体定位问题|尊敬的用户，您好，您的反馈已收到。非常抱歉，无法具体定位您的问题，您方便详细描述您的问题吗？方便提供录屏/歌曲文件等，以便为您排查修复。\n如有其他问题也可以联系我们，感谢您的支持和关注，祝您生活愉快！|\n\n|问题|参考回复|\n|-|-|\n|升级新版本后，本地歌曲排序错误|尊敬的用户，您好，您的反馈已收到。给您带来不便，非常抱歉。目前因版本升级，歌曲格式以及排序方式更多样化，导致本地歌曲部分排序可能无法同步，我们会尽快修复，感谢您的关注与支持，祝您生活愉快~|\n\n|问题|参考回复|\n|-|-|\n|本地歌曲按时间排序乱了/顺序不对|尊敬的用户，您好，您反馈的问题我们已经收到了，非常抱歉，给您不好的体验了，我们会尽快优化修复！\n如有其他问题也可以联系我们，感谢您的支持和关注，祝您生活愉快！|\n\n|问题|参考回复|\n|-|-|\n|关闭在线服务只只支持6.0.0.30及以上版本|尊敬的用户，您好，您的反馈已收到。给您带来不便，非常抱歉。目前“关闭在线服务”只支持6.0.0.30及以上版本，请您更新后体验，感谢您的支持与关注，祝您生活愉快~|\n\n|问题|参考回复|\n|-|-|\n|删除歌曲/删除歌单里的歌曲|尊敬的用户，您好，您的反馈已收到。如果您需要删除本地歌曲，可以点击本地歌曲列表，右侧的更多按钮，点击“删除”即可，请注意是否需要删除本地文件； 如果是需要删除歌单里的歌曲，需要在歌单的页面点击右侧更多按钮，可以批量操作歌曲。 \n如有其他问题也可以联系我们，感谢您的关注与支持，祝您生活愉快~|\n</context>"
#             # },
#             # {'role': 'user', 'content': '你好'},
#             # {'role': 'assistant', 'content': '您好,很高兴为您服务。请问您有什么需要帮助的吗?'},
#             # {'role': 'user', 'content': '你好'},
#             # {'role': 'assistant', 'content': '您好,很高兴为您服务。我是一个AI助手,随时为您提供帮助和解答。请问您有什么疑问或需要协助的地方吗?'},
#             # {'role': 'user', 'content': '你好'},
#             # {'role': 'assistant', 'content': '您好，很高兴再次见到您。请问有什么我可以帮助您的吗？如果您有任何问题或需要咨询的内容，请随时告诉我。'},
#             {'role': 'user', 'content': '今天天气怎么样？'},
#             {'role': 'assistant', 'content': '请问您想了解哪个城市的天气呢？'},
#             {'role': 'user', 'content': '上海'}
#         ],
#         'stream': False,
#         'model': 'Qwen2.5-72B-Instruct-AWQ'
#     }



# print(client.invoke(agent_pyload))



# from emd.sdk.clients.ecs_client import ECSClient

# client = ECSClient(
#     # model_id="Qwen2.5-72B-Instruct-AWQ"
#     # model_id="Qwen2.5-0.5B-Instruct"
#     base_url = "http://localhost:8080"
# )


# ret = client.invoke(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": [{"type": "text", "text": "9.11和9.9哪个更大？"}]

#             }
#         ],
#         "max_tokens": 512,
#         "temperature": 0.1,
#         "stream":False
#     }
# )
# print(ret)



# ret = client.invoke(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": [{"type": "text", "text": "9.11和9.9哪个更大？"}]

#             }
#         ],
#         "max_tokens": 512,
#         "temperature": 0.1,
#         "stream":True
#     }
# )
# # print(ret)
# for i in ret:
#     # print(i)

#     # print(i,i[-1]==ord("\n"))
#     print(i['choices'][0]['delta']['content'],end="")
