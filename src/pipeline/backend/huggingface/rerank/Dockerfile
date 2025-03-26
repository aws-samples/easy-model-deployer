FROM public.ecr.aws/aws-gcr-solutions/dmaa/huggingface/transformers-pytorch-gpu:{{VERSION}} AS huggingface-base

# Create a new stage based on vllm-base
FROM huggingface-base AS sagemaker-serving

# Ensure the serve script has executable permissions
# RUN chmod +x /usr/bin/serve
RUN pip install boto3 fastapi uvicorn modelscope
RUN pip install einops==0.8.0
RUN pip install flash-attn==2.7.4.post1 --no-build-isolation

# Expose port 8080
EXPOSE 8080
WORKDIR /opt/ml/code


# Set the serve script as the entrypoint
ENTRYPOINT ["/usr/bin/serve"]
