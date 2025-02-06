from dmaa import deploy

deploy(
    model_id="internlm2_5-20b-chat-4bit-awq",
    instance_type="g5.4xlarge",
    engine_type="vllm",
    service_type="sagemaker",
    region="us-west-2",
    extra_params={
        "vllm_cli_args":"--max_num_seqs 4 --max_model_len 16000 --disable-log-stats"
    }
)