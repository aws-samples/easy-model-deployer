from .. import Model

from ..services import (
    sagemaker_service,
    sagemaker_async_service,
    ecs_service,
    local_service
)
from ..frameworks import custom_framework
from ..instances import (
    g5d4xlarge_instance,
    local_instance
)
from ..engines import custom_engine

Model.register(
    dict(
        model_id = "Model-In-Docker",
        supported_engines=[custom_engine],
        supported_instances=[
            g5d4xlarge_instance,
            local_instance
        ],
        supported_services=[
            sagemaker_service,
            sagemaker_async_service,
            ecs_service,
            local_service
        ],
        supported_frameworks=[
            custom_framework
        ],
        allow_china_region=True,
        description="Custom model running in Docker container",
        need_prepare_model=False,
    )
)