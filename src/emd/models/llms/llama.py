from .. import Model
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
    local_instance
)
from ..engines import tgi_llama3d3_engine301
from emd.models.utils.constants import ModelType
from ..model_series import LLAMA3_SERIES


Model.register(
    dict(
        model_id="llama-3.3-70b-instruct-awq",
        supported_engines=[tgi_llama3d3_engine301],
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
        huggingface_model_id="casperhansen/llama-3.3-70b-instruct-awq",
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of Llama LLMs",
        model_type=ModelType.LLM,
        model_series=LLAMA3_SERIES

    )

)
