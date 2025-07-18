from .. import Model
from ..engines import vllm_qwen3_engin091, vllm_gme_qwen2vl_engine091, vllm_gme_qwen2vl_engine084_compat
from ..services import sagemaker_service,local_service,ecs_service
from ..frameworks import fastapi_framework
from ..instances import (
    g5dxlarge_instance,
    g5d2xlarge_instance,
    g5d4xlarge_instance,
    g5d8xlarge_instance,
    g5d12xlarge_instance,
    g5d16xlarge_instance,
    local_instance
)
from emd.models.utils.constants import ModelType
from emd.models import ModelSeries
from ..model_series import QWEN3_SERIES, GME_SERIES


Model.register(
    dict(
        model_id = "Qwen3-Embedding-0.6B",
        supported_engines=[vllm_qwen3_engin091],
        supported_instances=[
            g5dxlarge_instance,
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d16xlarge_instance,
            local_instance
        ],
        supported_services=[
            sagemaker_service,
            ecs_service,
            local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        allow_china_region=True,
        huggingface_model_id="Qwen/Qwen3-Embedding-0.6B",
        modelscope_model_id="Qwen/Qwen3-Embedding-0.6B",
        require_huggingface_token=False,
        application_scenario="RAG",
        model_type=ModelType.EMBEDDING,
        model_series=QWEN3_SERIES
    )
)

Model.register(
    dict(
        model_id = "Qwen3-Embedding-4B",
        supported_engines=[vllm_qwen3_engin091],
        supported_instances=[
            g5dxlarge_instance,
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d16xlarge_instance,
            local_instance
        ],
        supported_services=[
            sagemaker_service,
            ecs_service,
            local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        allow_china_region=True,
        huggingface_model_id="Qwen/Qwen3-Embedding-4B",
        modelscope_model_id="Qwen/Qwen3-Embedding-4B",
        require_huggingface_token=False,
        application_scenario="RAG",
        model_type=ModelType.EMBEDDING,
        model_series=QWEN3_SERIES
    )
)

Model.register(
    dict(
        model_id = "Qwen3-Embedding-8B",
        supported_engines=[vllm_qwen3_engin091],
        supported_instances=[
            g5dxlarge_instance,
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d16xlarge_instance,
            local_instance
        ],
        supported_services=[
            sagemaker_service,
            ecs_service,
            local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        allow_china_region=True,
        huggingface_model_id="Qwen/Qwen3-Embedding-8B",
        modelscope_model_id="Qwen/Qwen3-Embedding-8B",
        require_huggingface_token=False,
        application_scenario="RAG",
        model_type=ModelType.EMBEDDING,
        model_series=QWEN3_SERIES
    )
)

Model.register(
    dict(
        model_id = "gme-Qwen2-VL-7B-Instruct",
        supported_engines=[vllm_gme_qwen2vl_engine084_compat],
        supported_instances=[
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d12xlarge_instance,
            g5d16xlarge_instance,
            local_instance
        ],
        supported_services=[
            sagemaker_service,
            ecs_service,
            local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        allow_china_region=True,
        huggingface_model_id="Alibaba-NLP/gme-Qwen2-VL-7B-Instruct",
        modelscope_model_id="Alibaba-NLP/gme-Qwen2-VL-7B-Instruct",
        require_huggingface_token=False,
        application_scenario="Multimodal RAG, image-text retrieval, visual search",
        description="General Multimodal Embedding model based on Qwen2-VL architecture, supporting text, image, and image-text pair inputs for unified multimodal representation learning and retrieval tasks. Uses vLLM v0.8.4 for transformers compatibility.",
        model_type=ModelType.EMBEDDING,
        model_series=GME_SERIES
    )
)
