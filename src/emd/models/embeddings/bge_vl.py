from .. import Model
from ..engines import huggingface_embedding_engine449
from ..services import sagemaker_service, local_service, ecs_service
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
from ..model_series import BGE_SERIES


Model.register(
    dict(
        model_id="bge-vl-base",
        supported_engines=[huggingface_embedding_engine449],
        supported_instances=[
            g5dxlarge_instance,
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d16xlarge_instance,
            local_instance,
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
        huggingface_model_id="BAAI/BGE-VL-base",
        modelscope_model_id="BAAI/BGE-VL-base",
        require_huggingface_token=False,
        application_scenario="Multimodal RAG, composed image retrieval, visual search",
        model_type=ModelType.EMBEDDING,
        model_series=BGE_SERIES,
        description="BGE-VL-base is a multimodal embedding model that supports text, image, and text-image pair inputs for unified multimodal representation learning and cross-modal retrieval tasks. Lightweight with 149M parameters."
    )
)

Model.register(
    dict(
        model_id="bge-vl-large",
        supported_engines=[huggingface_embedding_engine449],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d16xlarge_instance,
            local_instance,
        ],
        supported_services=[
            ecs_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        allow_china_region=True,
        huggingface_model_id="BAAI/BGE-VL-large",
        modelscope_model_id="BAAI/BGE-VL-large",
        require_huggingface_token=False,
        application_scenario="Multimodal RAG, composed image retrieval, visual search",
        model_type=ModelType.EMBEDDING,
        model_series=BGE_SERIES,
        description="BGE-VL-large is a larger multimodal embedding model that supports text, image, and text-image pair inputs for high-performance multimodal representation learning and cross-modal retrieval tasks."
    )
)
