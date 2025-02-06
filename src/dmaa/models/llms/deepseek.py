from .. import Model 
from ..engines import (
    vllm_deepseek_r1_distill_qwen_engine071,
    vllm_deepseek_r1_distill_llama_engine071
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
from dmaa.models.utils.constants import ModelType
from dmaa.models.utils.constants import ModelType
from dmaa.models import ModelSeries
from ..model_series import DEEPSEEK_REASONING_MODEL
from ..engines import tgi_deepseek_r1_llama_70b_engine301
from dmaa.models.utils.constants import ModelType
from ..model_series import LLAMA3_SERIES


Model.register(
    dict(
        model_id = "DeepSeek-R1-Distill-Qwen-32B",
        supported_engines=[vllm_deepseek_r1_distill_qwen_engine071],
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
        allow_china_region=False,
        huggingface_model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        # modelscope_model_id="Qwen/Qwen2.5-32B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)

Model.register(
    dict(
        model_id = "DeepSeek-R1-Distill-Qwen-14B",
        supported_engines=[vllm_deepseek_r1_distill_qwen_engine071],
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
        allow_china_region=False,
        huggingface_model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        # modelscope_model_id="Qwen/Qwen2.5-14B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)

Model.register(
    dict(
        model_id = "DeepSeek-R1-Distill-Qwen-7B",
        supported_engines=[vllm_deepseek_r1_distill_qwen_engine071],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d16xlarge_instance,
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
        allow_china_region=False,
        huggingface_model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        # modelscope_model_id="Qwen/Qwen2.5-14B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)

Model.register(
    dict(
        model_id = "DeepSeek-R1-Distill-Qwen-1.5B",
        supported_engines=[vllm_deepseek_r1_distill_qwen_engine071],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d16xlarge_instance,
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
        allow_china_region=False,
        huggingface_model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        # modelscope_model_id="Qwen/Qwen2.5-14B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)

Model.register(
    dict(
        model_id = "DeepSeek-R1-Distill-Llama-8B",
        supported_engines=[vllm_deepseek_r1_distill_llama_engine071],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d16xlarge_instance,
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
        allow_china_region=False,
        huggingface_model_id="deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        # modelscope_model_id="Qwen/Qwen2.5-14B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)


Model.register(
    dict(
        model_id = "deepseek-r1-distill-llama-70b-awq",
        supported_engines=[tgi_deepseek_r1_llama_70b_engine301,vllm_deepseek_r1_distill_llama_engine071],
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
        huggingface_endpoint = "https://hf-mirror.com",
        huggingface_model_id="casperhansen/deepseek-r1-distill-llama-70b-awq",
        # modelscope_model_id="Qwen/Qwen2.5-14B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)