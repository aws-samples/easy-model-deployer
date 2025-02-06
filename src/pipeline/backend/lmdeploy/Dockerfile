FROM public.ecr.aws/aws-gcr-solutions/dmaa/openmmlab/lmdeploy:{{VERSION}} AS lmdeploy-base

# Create a new stage based on vllm-base
FROM lmdeploy-base AS sagemaker-serving

# Ensure the serve script has executable permissions
# RUN chmod +x /usr/bin/serve
RUN pip3 install boto3

# Expose port 8080
EXPOSE 8080
WORKDIR /opt/ml/code


# Set the serve script as the entrypoint
ENTRYPOINT ["/usr/bin/serve"]