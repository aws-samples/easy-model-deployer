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
from ..engines import vllm_internlm2d5_engine064
from emd.models.utils.constants import ModelType
from emd.models import ModelSeries
from ..model_series import INTERLM2d5_SERIES

Model.register(
    dict(
        model_id = "internlm2_5-20b-chat-4bit-awq",
        supported_engines=[vllm_internlm2d5_engine064],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d12xlarge_instance,
            g5d16xlarge_instance,
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
        allow_china_region=True,
        supported_frameworks=[fastapi_framework],
        huggingface_model_id="internlm/internlm2_5-20b-chat-4bit-awq",
        modelscope_model_id="ticoAg/internlm2_5-20b-chat-awq",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="internlm2_5-20b-chat-4bit-awq",
        model_type=ModelType.LLM,
        model_series=INTERLM2d5_SERIES
    )
)

Model.register(
    dict(
        model_id = "internlm2_5-20b-chat",
        supported_engines=[vllm_internlm2d5_engine064],
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
        allow_china_region=True,
        supported_frameworks=[fastapi_framework],
        huggingface_model_id="internlm/internlm2_5-20b-chat",
        modelscope_model_id="Shanghai_AI_Laboratory/internlm2_5-20b-chat",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="internlm2_5-20b-chat",
        model_type=ModelType.LLM,
        model_series=INTERLM2d5_SERIES
    )
)

Model.register(
    dict(
        model_id = "internlm2_5-7b-chat",
        supported_engines=[vllm_internlm2d5_engine064],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d12xlarge_instance,
            g5d16xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
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
        allow_china_region=True,
        supported_frameworks=[fastapi_framework],
        huggingface_model_id="internlm/internlm2_5-7b-chat",
        modelscope_model_id="Shanghai_AI_Laboratory/internlm2_5-7b-chat",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="internlm2_5-7b-chat",
        model_type=ModelType.LLM,
        model_series=INTERLM2d5_SERIES
    )
)

Model.register(
    dict(
        model_id = "internlm2_5-7b-chat-4bit",
        supported_engines=[vllm_internlm2d5_engine064],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d12xlarge_instance,
            g5d16xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
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
        supported_frameworks=[fastapi_framework],
        huggingface_model_id="internlm/internlm2_5-7b-chat-4bit",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="internlm2_5-7b-chat-4bit",
        model_type=ModelType.LLM,
        model_series=INTERLM2d5_SERIES
    )
)

Model.register(
    dict(
        model_id = "internlm2_5-1_8b-chat",
        supported_engines=[vllm_internlm2d5_engine064],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d12xlarge_instance,
            g5d16xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
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
        allow_china_region=True,
        supported_frameworks=[fastapi_framework],
        huggingface_model_id="internlm/internlm2_5-1_8b-chat",
        modelscope_model_id="Shanghai_AI_Laboratory/internlm2_5-1_8b-chat",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="internlm2_5-1_8b-chat",
        model_type=ModelType.LLM,
        model_series=INTERLM2d5_SERIES
    )
)
