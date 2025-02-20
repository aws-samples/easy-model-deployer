from emd.sdk.deploy import deploy

deploy(
    model_id="glm-4-9b-chat-GPTQ-Int4",
    instance_type="g5.4xlarge",
    engine_type="vllm",
    service_type="sagemaker",
    region="us-west-2",
    extra_params={
        "vllm_cli_args":"--max_num_seqs 4 --max_model_len 16000 --disable-log-stats"
    },
    force_env_stack_update=True
)
