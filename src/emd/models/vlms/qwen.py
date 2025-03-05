from .. import Model
from ..engines import (
    vllm_qwen2vl7b_engine064,
    vllm_qwen2vl72b_engine064,
    vllm_qwen25vl72b_engine073
)
from ..services import (
    sagemaker_service,
    sagemaker_async_service,
    ecs_service,
    local_service
)
from ..frameworks import fastapi_framework
from ..instances import (
    g5d2xlarge_instance,
    g5d4xlarge_instance,
    g5d8xlarge_instance,
    g5d12xlarge_instance,
    g5d16xlarge_instance,
    g5d24xlarge_instance,
    g5d48xlarge_instance,
    g6e2xlarge_instance,
    local_instance
)
from emd.models.utils.constants import ModelType
from ..model_series import QWEN2VL_SERIES,QWEN_REASONING_MODEL


Model.register(
    dict(
        model_id = "Qwen2-VL-72B-Instruct-AWQ",
        supported_engines=[vllm_qwen2vl72b_engine064],
        supported_instances=[
            g5d12xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
            local_instance
        ],
        supported_services=[
            sagemaker_service, sagemaker_async_service,local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        allow_china_region=True,
        huggingface_model_id="Qwen/Qwen2-VL-72B-Instruct-AWQ",
        modelscope_model_id="Qwen/Qwen2-VL-72B-Instruct-AWQ",
        require_huggingface_token=False,
        application_scenario="vision llms for image understanding",
        description="The latest series of Qwen2 VL",
        model_type=ModelType.VLM,
        model_series=QWEN2VL_SERIES
    )
)


Model.register(
    dict(
        model_id = "Qwen2.5-VL-72B-Instruct-AWQ",
        supported_engines=[vllm_qwen25vl72b_engine073],
        supported_instances=[
            g5d12xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
            local_instance
        ],
        supported_services=[
            sagemaker_service,
            sagemaker_async_service,
            local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        allow_china_region=True,
        huggingface_model_id="Qwen/Qwen2.5-VL-72B-Instruct-AWQ",
        modelscope_model_id="Qwen/Qwen2.5-VL-72B-Instruct-AWQ",
        require_huggingface_token=False,
        application_scenario="vision llms for image understanding",
        description="The latest series of Qwen2.5 VL",
        model_type=ModelType.VLM,
        model_series=QWEN2VL_SERIES
    )
)

Model.register(
    dict(
        model_id = "QVQ-72B-Preview-AWQ",
        supported_engines=[vllm_qwen2vl72b_engine064],
        supported_instances=[
            g5d12xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
            local_instance
        ],
        supported_services=[
            sagemaker_service, sagemaker_async_service,local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        huggingface_model_id="kosbu/QVQ-72B-Preview-AWQ",
        require_huggingface_token=False,
        application_scenario="vision llms for complex image understanding",
        description="The latest reasoning model of Qwen2 VL",
        model_type=ModelType.VLM,
        model_series=QWEN_REASONING_MODEL
    )
)


Model.register(
    dict(
        model_id = "Qwen2-VL-7B-Instruct",
        supported_engines=[vllm_qwen2vl7b_engine064],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d12xlarge_instance,
            g5d16xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
            g6e2xlarge_instance,
            local_instance
        ],
        supported_services=[
            sagemaker_service, sagemaker_async_service,local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        allow_china_region=True,
        huggingface_model_id="Qwen/Qwen2-VL-7B-Instruct",
        modelscope_model_id="Qwen/Qwen2-VL-7B-Instruct",
        require_huggingface_token=False,
        application_scenario="vision llms for image understanding",
        description="The latest series of Qwen2 VL",
        model_type=ModelType.VLM,
        model_series=QWEN2VL_SERIES
    )
)
