from .. import Model
from ..engines import (
    huggingface_baichuan_engine_4d41d2,
    vllm_M1_14B_engine066
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
    inf2d8xlarge_instance,
    local_instance
)
from emd.models.utils.constants import ModelType
from emd.models.utils.constants import ModelType
from emd.models import ModelSeries
from ..model_series import BAICHAUN_SERIES


Model.register(
    dict(
        model_id = "Baichuan-M1-14B-Instruct",
        supported_engines=[vllm_M1_14B_engine066,huggingface_baichuan_engine_4d41d2],
        supported_instances=[
            g5d12xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
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
        huggingface_model_id="baichuan-inc/Baichuan-M1-14B-Instruct",
        # modelscope_model_id="Qwen/QwQ-32B-Preview",
        require_huggingface_token=False,
        application_scenario="chat/translation",
        description="medical domain LLM",
        model_type=ModelType.LLM,
        model_series=BAICHAUN_SERIES
    )
)
