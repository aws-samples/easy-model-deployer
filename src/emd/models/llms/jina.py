from .. import Model
from ..engines import (
    vllm_qwen2d5_engine064,
    vllm_qwen2d5_128k_engine064,
    huggingface_llm_engine_4d41d2,
    tgi_qwen2d5_72b_engine064,
    tgi_qwen2d5_on_inf2,
    tgi_qwen2d5_72b_on_inf2,
    vllm_qwen2d5_72b_engine064,
    vllm_qwq_engine073
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
    g4dn2xlarge_instance,
    g6e2xlarge_instance,
    inf2d8xlarge_instance,
    inf2d24xlarge_instance,
    local_instance
)
from emd.models.utils.constants import ModelType
from emd.models.utils.constants import ModelType
from emd.models import ModelSeries
from ..model_series import JINA_SERIES


Model.register(
    dict(
        model_id = "ReaderLM-v2",
        supported_engines=[
            vllm_qwen2d5_engine064,
            tgi_qwen2d5_on_inf2
            ],
        supported_instances=[
            g4dn2xlarge_instance,
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            # g5d12xlarge_instance,
            g5d16xlarge_instance,
            # g5d24xlarge_instance,
            # g5d48xlarge_instance,
            inf2d8xlarge_instance,
            local_instance
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
        huggingface_model_id="jinaai/ReaderLM-v2",
        modelscope_model_id="jinaai/ReaderLM-v2",
        require_huggingface_token=False,
        application_scenario="Html information extraction",
        description="ReaderLM-v2 is a 1.5B parameter language model that converts raw HTML into beautifully formatted markdown or JSON with superior accuracy and improved longer context handling. Supporting multiple languages (29 in total), ReaderLM-v2 is specialized for tasks involving HTML parsing, transformation, and text extraction.",
        model_type=ModelType.LLM,
        model_series=JINA_SERIES,
    )
)
