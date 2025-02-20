from .. import Model
from ..engines import lmdeploy_intervl2d5_awq_engine064
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
from ..model_series import INTERNVL25_SERIES


Model.register(
    dict(
        model_id = "InternVL2_5-78B-AWQ",
        supported_engines=[lmdeploy_intervl2d5_awq_engine064],
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
        huggingface_model_id="OpenGVLab/InternVL2_5-78B-AWQ",
        require_huggingface_token=False,
        application_scenario="vision llms for image understanding",
        description="The latest series of Intervl2.5",
        model_type=ModelType.VLM,
        model_series=INTERNVL25_SERIES,
    )
)
