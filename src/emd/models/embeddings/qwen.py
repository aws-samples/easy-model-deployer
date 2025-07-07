from .. import Model
from ..engines import vllm_qwen3_engin091
from ..services import sagemaker_service,local_service,ecs_service
from ..frameworks import fastapi_framework
from ..instances import (
    g5dxlarge_instance,
    g5d2xlarge_instance,
    g5d4xlarge_instance,
    g5d8xlarge_instance,
    g5d16xlarge_instance,
    local_instance
)
from emd.models.utils.constants import ModelType
from emd.models import ModelSeries
from ..model_series import QWEN3_SERIES


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
