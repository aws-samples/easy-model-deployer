from dmaa.integrations.langchain_clients import SageMakerVllmChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
from langchain.tools.base import StructuredTool
from langchain_core.utils.function_calling import (
    convert_to_openai_function,
    convert_to_openai_tool
)

chat_model = SageMakerVllmChatModel(
    # region_name='us-west-2',
    # endpoint_name="DMAA-Model-Qwen2-5-7B-Instruct-r8av5c-endpoint"
    # model_id="Qwen2.5-0.5B-Instruct",
    # model_id="Qwen2.5-0.5B-Instruct",
    # model_id="Qwen2.5-7B-Instruct",
    # model_id="Qwen2.5-72B-Instruct-AWQ",
    # model_tag='Admin',
    # model_id="internlm2_5-20b-chat",
    # model_id="internlm2_5-20b-chat-4bit-awq",
    # model_id="internlm2_5-20b-chat",
    # model_id="internlm2_5-20b-chat-4bit-awq",
    model_id="DeepSeek-R1-Distill-Qwen-32B",
    model_kwargs={
        "temperature":0.5,
        # "repetition_penalty":1.05,
        # "chat_template": open("/efs/projects/deploy-model-anywhere-on-aws/src/pipeline/backend/vllm/chat_templates/deepseek_32b_chat_template.jinja").read()
    }
    # model_tag='Admin',
    # endpoint_name="DMAA-Model-Qwen2-5-72B-Instruct-AWQ-sv1dqz-endpoint"
) 


chain = chat_model | StrOutputParser()

messages = [
        HumanMessage(content="9.11和9.9两个数字哪个更大？"),
        # AIMessage(content="<thinking>"),
    ]
print(chain.invoke(messages))

# print(sfgsfd)
print("="*50)


# stream test
print('stream test')
for i in chain.stream(messages):
    print(i,end="",flush=True)


print("="*50)

# tool use test 
def calculate_sentence_len(char:str,sentence:str):
    """calculate the sentence length"""
    c = 0
    for i in sentence:
        if i == char:
            c += 1
    return c


tool = StructuredTool.from_function(
    func=calculate_sentence_len,
    name="count_char_num",
    description="count the char num in a give sentence"
)

# chat_model_with_tool = chat_model.bind_tools([tool],tool_choice="calculate_sentence_len")
chat_model_with_tool = chat_model.bind_tools([tool])


messages = [
    SystemMessage(content="You are a helpful AI agent, you are goods at applying certainly tools to solve kinds of questions."),
        # AIMessage(content="<thinking>"),
    
    HumanMessage(content="how many 'r’s in ‘strrawberries’"),
        # AIMessage(content="<thinking>"),
    ]
print(chat_model_with_tool.invoke(
    messages

    # "how many 'r’s in ‘strrawberries’",
    # extra_body={
    #     "repetition_penalty":1.05,
    #     "chat_template": open("/efs/projects/deploy-model-anywhere-on-aws/src/pipeline/backend/vllm/chat_templates/qwen_2d5_add_prefill_chat_template.jinja").read()
    # }

))


# vlm model test 

# chat_model = SageMakerVllmChatModel(
#     # region_name='us-west-2',
#     # endpoint_name="DMAA-Model-Qwen2-5-7B-Instruct-r8av5c-endpoint"
#     # model_id="Qwen2.5-0.5B-Instruct",
#     # model_id="Qwen2.5-0.5B-Instruct",
#     # model_id="Qwen2.5-7B-Instruct",
#     # model_id="Qwen2.5-72B-Instruct-AWQ",
#     # model_tag='Admin',
#     # model_id="internlm2_5-20b-chat",
#     # model_id="internlm2_5-20b-chat-4bit-awq",
#     # model_id="internlm2_5-20b-chat",
#     model_id="Qwen2-VL-7B-Instruct",
#     # model_id="internlm2_5-20b-chat-4bit-awq",
#     # model_tag='Admin',
#     # endpoint_name="DMAA-Model-Qwen2-5-72B-Instruct-AWQ-sv1dqz-endpoint"
# ) 


# chain = chat_model | StrOutputParser()

# image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"


# messages = [
#         HumanMessage(
#             content=[
#                 {"type": "text", "text": "What’s in this image?"},
#                 {"type": "image_url", "image_url": {"url": image_url}},
#             ]
#     ),
#         # AIMessage(content="<thinking>"),
#     ]
# print(chain.invoke(messages))

