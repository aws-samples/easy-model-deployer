from .. import Model

from ..services import (
    sagemaker_service,
)
from ..frameworks import custom_framework
from ..instances import (
    g4dnxlarge_instance,
    g4dn2xlarge_instance,
    g4dn4xlarge_instance,
    g4dn8xlarge_instance,
    g4dn12xlarge_instance,
    g4dn16xlarge_instance,
    g5dxlarge_instance,
    g5d2xlarge_instance,
    g5d4xlarge_instance,
    g5d8xlarge_instance,
    g5d12xlarge_instance,
    local_instance
)
from ..engines import custom_engine
from ..utils.constants import CUSTOM_DOCKER_MODEL_ID

Model.register(
    dict(
        model_id = CUSTOM_DOCKER_MODEL_ID,
        supported_engines=[custom_engine],
        supported_instances=[
            g4dnxlarge_instance,
            g4dn2xlarge_instance,
            g4dn4xlarge_instance,
            g4dn8xlarge_instance,
            g4dn12xlarge_instance,
            g4dn16xlarge_instance,
            g5dxlarge_instance,
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d12xlarge_instance,
            local_instance
        ],
        supported_services=[
            sagemaker_service,
        ],
        supported_frameworks=[
            custom_framework
        ],
        allow_china_region=True,
        description="Custom model running in Docker container",
        need_prepare_model=False,
    )
)
