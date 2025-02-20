from emd import deploy


deploy(
    model_id="Qwen2.5-0.5B-Instruct",
    instance_type="g5.2xlarge",
    engine_type="vllm",
    service_type="sagemaker",
    region="us-west-2",
    # extra_params={
    #     "vllm_cli_args":"--max_num_seqs 20 --max_model_len 16000 --disable-log-stats"
    # }
)


# deploy(
#     model_id="Qwen2.5-7B-Instruct",
#     instance_type="g5.4xlarge",
#     engine_type="vllm",
#     service_type="sagemaker",
#     region="us-west-2",
#     extra_params={
#         "vllm_cli_args":"--max_num_seqs 20 --max_model_len 16000 --disable-log-stats"
#     }
# )
# deploy(
#     model_id="Qwen2.5-7B-Instruct",
#     model_id="Qwen2.5-72B-Instruct-AWQ",
#     instance_type="g5.12xlarge",
#     engine_type="vllm",
#     service_type="sagemaker",
#     region="us-west-2",
#     extra_params={
#         "vllm_cli_args":"--max_num_seqs 20 --max_model_len 16000 --disable-log-stats"
#     }
# )
