import json

from service.ec2.client import EC2Client
from service.sagemaker.client import SageMakerClient

request = {
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {
            "role": "assistant",
            "content": "The Los Angeles Dodgers won the World Series in 2020.",
        },
        {
            "role": "user",
            "content": "Where was it played? The answer should be as long as possible.",
        },
    ],
    "model": "Qwen/Qwen2-beta-7B-Chat",
    # "model": "Qwen/Qwen2.5-72B-Instruct-AWQ",
    # "model": "deepseek-ai/deepseek-llm-7b-chat",
    # "stream": False,
}

if __name__ == "__main__":
    # Initialize clients
    invoke_vllm_sagemaker_client = SageMakerClient(
        region="us-east-1",
        # region="cn-north-1",
        # endpoint_name="Qwen-Qwen2-5-72B-Instruct-AWQ-vllm-2024-11-11-08-04-56",
        # endpoint_name="Qwen-Qwen2-5-72B-Instruct-AWQ-vllm-2024-11-15-06-11-08",
        endpoint_name="Qwen-Qwen2-beta-7B-Chat-vllm-2024-11-24-02-23-10",
        # endpoint_name="Qwen-Qwen2-beta-7B-Chat-vllm-2024-11-15-03-45-30",
        stream=True,
        # model="Qwen/Qwen2.5-72B-Instruct-AWQ",
        model="Qwen/Qwen2-beta-7B-Chat",
    )
    invoke_vllm_ec2_client = EC2Client(
        host="localhost", stream=True, model="Qwen/Qwen2-beta-7B-Chat"
    )

    # Test invoke
    invoke_vllm_sagemaker_client.invoke(request)
    # invoke_vllm_ec2_client.invoke(request)

    # invoke_vllm_sagemaker_stream_client.invoke(request)
    # with open("src/invoke/workflow_api_animatediff.json") as f:
    #     prompt = json.load(f)
    #     invoke_comfy_ui_ec2_client.invoke(prompt)
