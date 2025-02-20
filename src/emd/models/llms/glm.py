from .. import Model
from ..engines import vllm_glm4_engine064,vllm_glm4_wo_flashinfer_engine064
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

from emd.models.utils.constants import ModelType
from ..model_series import GLM4_SERIES

# Model.register(
#     dict(
#         model_id = "glm-4-9b-chat-GPTQ-Int4",
#         supported_engines=[vllm_glm4_wo_flashinfer_engine064],
#         supported_instances=[
#             g5d2xlarge_instance,
#             g5d4xlarge_instance,
#             g5d8xlarge_instance,
#             g5d12xlarge_instance,
#             g5d16xlarge_instance,
#             g5d24xlarge_instance,
#             g5d48xlarge_instance,
#             local_instance
#         ],
#         supported_services=[
#             sagemaker_service,
#             sagemaker_async_service,
#             ecs_service,
#             local_service
#         ],
#         allow_china_region=True,
#         supported_frameworks=[fastapi_framework],
#         huggingface_model_id="model-scope/glm-4-9b-chat-GPTQ-Int4",
#         modelscope_model_id="tclf90/glm-4-9b-chat-GPTQ-Int4",
#         require_huggingface_token=False,
#         application_scenario="Agent, tool use, translation, summary",
#         description="glm-4-9b-chat-GPTQ-Int4",
#         model_type=ModelType.LLM,
#         model_series=GLM4_SERIES
#     )
# )

Model.register(
    dict(
        model_id = "glm-4-9b-chat",
        supported_engines=[vllm_glm4_engine064],
        supported_instances=[
            g5d12xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
        ],
        supported_services=[
            sagemaker_service,
            sagemaker_async_service,
            ecs_service,
            local_service
        ],
        allow_china_region=True,
        supported_frameworks=[fastapi_framework],
        huggingface_model_id="THUDM/glm-4-9b-chat",
        modelscope_model_id="ZhipuAI/glm-4-9b-chat",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="glm-4-9b-chat-GPTQ-Int4",
        model_type=ModelType.LLM,
        model_series=GLM4_SERIES
    )
)
