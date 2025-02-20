import json

from src.backend.vllm.vllm_transformer import VLLMEC2Client, VLLMSageMakerClient
from src.backend.comfyui.comfy_ui_transformer import ComfyUISageMakerClient, ComfyUIEC2Client

request = {
    "messages": [{
        "role": "system",
        "content": "You are a helpful assistant."
    }, {
        "role": "user",
        "content": "Who won the world series in 2020?"
    }, {
        "role":
        "assistant",
        "content":
        "The Los Angeles Dodgers won the World Series in 2020."
    }, {
        "role": "user",
        "content": "Where was it played? The answer should be as long as possible."
    }],
    "model": "Qwen/Qwen2-beta-7B-Chat",
    # "model": "deepseek-ai/deepseek-llm-7b-chat",
    # "stream": False,
}

if __name__ == "__main__":
    # Initialize clients
    invoke_vllm_ec2_stream_client = VLLMEC2Client(host="http://localhost:9000", stream=True)
    invoke_vllm_ec2_client = VLLMEC2Client(host="http://0.0.0.0:9000", stream=False)
    invoke_vllm_sagemaker_stream_client = VLLMSageMakerClient(endpoint_name="emd-vllm-on-sagemaker", stream=True)
    invoke_vllm_sagemaker_client = VLLMSageMakerClient(endpoint_name="emd-vllm-on-sagemaker", stream=False)
    invoke_comfy_ui_ec2_client = ComfyUIEC2Client(host="http://0.0.0.0:9000")
    invoke_comfy_ui_sagemaker_client = ComfyUISageMakerClient(endpoint_name="vllm-on-sagemaker-4")

    # Test invoke
    # invoke_vllm_ec2_client.invoke(request)
    # invoke_vllm_ec2_stream_client.invoke(request)
    invoke_vllm_sagemaker_client.invoke(request)
    # invoke_vllm_sagemaker_stream_client.invoke(request)
    # with open("src/invoke/workflow_api_animatediff.json") as f:
    #     prompt = json.load(f)
    #     invoke_comfy_ui_ec2_client.invoke(prompt)
