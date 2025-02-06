FROM public.ecr.aws/aws-gcr-solutions/dmaa/huggingface/transformers-pytorch-gpu:{{VERSION}} AS huggingface-base

# Create a new stage based on vllm-base
FROM huggingface-base AS sagemaker-serving

# Ensure the serve script has executable permissions
# RUN chmod +x /usr/bin/serve
RUN pip install boto3 fastapi uvicorn

# Expose port 8080
EXPOSE 8080
WORKDIR /opt/ml/code


# Set the serve script as the entrypoint
ENTRYPOINT ["/usr/bin/serve"]