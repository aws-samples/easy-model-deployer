from .. import Model
from ..engines import ktransformers_engine
from ..services import (
    sagemaker_service,
    sagemaker_async_service,
    ecs_service,
    local_service
)
from ..frameworks import fastapi_framework
from ..instances import (
    g6e24xlarge_instance,
    g6e48xlarge_instance,
    local_instance
)
from emd.models.utils.constants import ModelType
from ..model_series import KIMI_SERIES

Model.register(
    dict(
        model_id="Kimi-K2-Instruct-Q4_K_M-GGUF",
        supported_engines=[ktransformers_engine],
        supported_instances=[
            g6e24xlarge_instance,  # 4 GPUs, 96 vCPU, 768GB RAM - Minimum viable
            g6e48xlarge_instance,  # 8 GPUs, 192 vCPU, 1536GB RAM - Optimal
            local_instance         # Local deployment (600GB+ RAM required)
        ],
        supported_services=[
            sagemaker_service,
            sagemaker_async_service,
            ecs_service,
            local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        allow_china_region=True,
        huggingface_model_id="KVCache-ai/Kimi-K2-Instruct-GGUF",
        huggingface_model_download_kwargs=dict(allow_patterns=["*Q4_K_M*"]),
        require_huggingface_token=False,
        application_scenario="Agentic AI, tool use, reasoning, coding, autonomous problem-solving",
        description="Kimi K2 1T parameter MoE model with 32B activated parameters in GGUF Q4_K_M format. Optimized for KTransformers deployment with 600GB+ RAM requirement. Achieves 10-14 TPS performance.",
        model_type=ModelType.LLM,
        model_series=KIMI_SERIES,
        need_prepare_model=False
    )
)