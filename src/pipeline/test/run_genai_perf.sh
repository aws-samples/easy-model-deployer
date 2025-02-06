export RELEASE="24.10"

docker run -it --net=host --gpus=all  nvcr.io/nvidia/tritonserver:${RELEASE}-py3-sdk

# Check out genai_perf command inside the container:
genai-perf --help

genai-perf profile --service-kind openai --url localhost:9000 -m Qwen/Qwen2.5-7B-Instruct --endpoint-type chat --concurrency 10 --generate-plots