FROM public.ecr.aws/aws-gcr-solutions/dmaa/huggingface/text-generation-inference:{{VERSION}} AS tgi-base

# Create a new stage based on vllm-base
FROM tgi-base AS sagemaker-serving

# Ensure the serve script has executable permissions
# RUN chmod +x /usr/bin/serve
RUN pip install boto3 fastapi uvicorn requests openai

# Expose port 8080
EXPOSE 8080
WORKDIR /opt/ml/code


# Set the serve script as the entrypoint
ENTRYPOINT ["/usr/bin/serve"]