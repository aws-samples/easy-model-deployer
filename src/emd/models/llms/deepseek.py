from .. import Model
from ..engines import (
    vllm_deepseek_r1_distill_qwen_engine071,
    vllm_deepseek_r1_distill_qwen_engine085,
    vllm_deepseek_r1_distill_llama_engine071,
    ollama_deepseek_r1_qwen2d5_1d5b_engine057,
    llama_cpp_deepseek_r1_1d58_bit_engine_b9ab0a4,
    llama_cpp_deepseek_r1_distill_engineb9ab0a4,
    tgi_deepseek_r1_llama_70b_engine301,
    ktransformers_engine,
    vllm_deepseek_r1_engine084
)
from ..services import (
    sagemaker_service,
    sagemaker_async_service,
    ecs_service,
    local_service
)
from ..frameworks import fastapi_framework
from ..instances import (
    g5dxlarge_instance,
    g5d2xlarge_instance,
    g5d4xlarge_instance,
    g5d8xlarge_instance,
    g5d12xlarge_instance,
    g5d16xlarge_instance,
    g5d24xlarge_instance,
    g5d48xlarge_instance,
    g6d2xlarge_instance,
    g6d4xlarge_instance,
    g6d8xlarge_instance,
    g6d12xlarge_instance,
    g6d16xlarge_instance,
    g6d24xlarge_instance,
    g6d48xlarge_instance,
    g6e2xlarge_instance,
    g6e4xlarge_instance,
    g6e8xlarge_instance,
    g6e12xlarge_instance,
    g6e16xlarge_instance,
    g6e24xlarge_instance,
    g6e48xlarge_instance,
    inf2d8xlarge_instance,
    local_instance
)
from emd.models.utils.constants import ModelType
from emd.models.utils.constants import ModelType
from emd.models import ModelSeries
from ..model_series import DEEPSEEK_REASONING_MODEL,DEEPSEEK_V3_SERIES
from ..engines import tgi_deepseek_r1_llama_70b_engine301
from emd.models.utils.constants import ModelType
from ..model_series import LLAMA3_SERIES


Model.register(
    dict(
        model_id = "DeepSeek-R1-Distill-Qwen-32B",
        supported_engines=[
            vllm_deepseek_r1_distill_qwen_engine071,
            tgi_deepseek_r1_llama_70b_engine301
        ],
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
        huggingface_model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        modelscope_model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
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
        allow_china_region=True,
        huggingface_model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        modelscope_model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
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
        allow_china_region=True,
        huggingface_model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        modelscope_model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
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
        allow_china_region=True,
        huggingface_model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        modelscope_model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)

Model.register(
    dict(
        model_id = "DeepSeek-R1-Distill-Qwen-1.5B_ollama",
        supported_engines=[ollama_deepseek_r1_qwen2d5_1d5b_engine057],
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
        allow_china_region=True,
        ollama_model_id="deepseek-r1:1.5b",
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
        model_id = "DeepSeek-R1-Distill-Qwen-1.5B-GGUF",
        supported_engines=[llama_cpp_deepseek_r1_distill_engineb9ab0a4],
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
        huggingface_model_id = "unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF",
        huggingface_model_download_kwargs = {
            "allow_patterns":["DeepSeek-R1-Distill-Qwen-1.5B-Q8_0.gguf"],
        },
        allow_china_region=True,
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)

Model.register(
    dict(
        model_id = "DeepSeek-R1-Distill-Qwen-32B-GGUF",
        supported_engines=[llama_cpp_deepseek_r1_distill_engineb9ab0a4],
        supported_instances=[
            g5d12xlarge_instance,
            g5d24xlarge_instance,
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
        huggingface_model_id = "unsloth/DeepSeek-R1-Distill-Qwen-32B-GGUF",
        huggingface_model_download_kwargs = {
            "allow_patterns":["DeepSeek-R1-Distill-Qwen-32B-Q8_0.gguf"],
        },
        allow_china_region=True,
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
        allow_china_region=True,
        huggingface_model_id="deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        modelscope_model_id="deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)

Model.register(
    dict(
        model_id = "DeepSeek-R1-0528-Qwen3-8B",
        supported_engines=[vllm_deepseek_r1_distill_qwen_engine085],
        supported_instances=[
            g5dxlarge_instance,
            g5d2xlarge_instance,
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
            fastapi_framework
        ],
        allow_china_region=True,
        huggingface_model_id="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
        modelscope_model_id="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="DeepSeek R1 got a minor upgrade (now DeepSeek-R1-0528). It does great in math, programming, and logic tests, almost as good as top models like O3 and Gemini 2.5 Pro.",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)

Model.register(
    dict(
        model_id = "deepseek-r1-distill-llama-70b-awq",
        supported_engines=[vllm_deepseek_r1_distill_llama_engine071,tgi_deepseek_r1_llama_70b_engine301],
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
        # huggingface_endpoints = ["https://huggingface.co","https://hf-mirror.com"],
        huggingface_model_id="casperhansen/deepseek-r1-distill-llama-70b-awq",
        # modelscope_model_id="Qwen/Qwen2.5-14B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)

# Model.register(
#     dict(
#         model_id = "deepseek-r1-671b-1.58bit_ollama",
#         supported_engines=[ollama_deepseek_r1_qwen2d5_1d5b_engine057],
#         supported_instances=[
#             g5d48xlarge_instance,
#             local_instance
#         ],
#         supported_services=[
#             sagemaker_service,
#             sagemaker_async_service,
#             ecs_service,
#             local_service
#         ],
#         supported_frameworks=[
#             fastapi_framework
#         ],
#         allow_china_region=False,
#         ollama_model_id="SIGJNF/deepseek-r1-671b-1.58bit",
#         # modelscope_model_id="Qwen/Qwen2.5-14B-Instruct",
#         require_huggingface_token=False,
#         application_scenario="Agent, tool use, translation, summary",
#         description="The latest series of DeepSeek LLMs for reasoning",
#         model_type=ModelType.LLM,
#         model_series=DEEPSEEK_REASONING_MODEL
#     )
# )


Model.register(
    dict(
        model_id = "deepseek-r1-671b-1.58bit_gguf",
        supported_engines=[llama_cpp_deepseek_r1_1d58_bit_engine_b9ab0a4, ktransformers_engine],
        supported_instances=[
            g5d8xlarge_instance,
            g5d12xlarge_instance,
            g5d16xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
            g6d8xlarge_instance,
            g6d12xlarge_instance,
            g6d16xlarge_instance,
            g6d24xlarge_instance,
            g6d48xlarge_instance,
            g6e4xlarge_instance,
            g6e8xlarge_instance,
            g6e12xlarge_instance,
            g6e16xlarge_instance,
            g6e24xlarge_instance,
            g6e48xlarge_instance,
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
        need_prepare_model=False,
        huggingface_model_id="unsloth/DeepSeek-R1-GGUF",
        huggingface_model_download_kwargs = dict(allow_patterns = ["*UD-IQ1_S*"]),
        modelscope_model_id="unsloth/DeepSeek-R1-GGUF",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)

Model.register(
    dict(
        model_id = "deepseek-r1-671b-2.51bit_gguf",
        supported_engines=[ktransformers_engine],
        supported_instances=[
            g5d12xlarge_instance,
            g5d16xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
            g6d12xlarge_instance,
            g6d16xlarge_instance,
            g6d24xlarge_instance,
            g6d48xlarge_instance,
            g6e8xlarge_instance,
            g6e12xlarge_instance,
            g6e16xlarge_instance,
            g6e24xlarge_instance,
            g6e48xlarge_instance,
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
        need_prepare_model=False,
        huggingface_model_id="unsloth/DeepSeek-R1-GGUF",
        huggingface_model_download_kwargs = dict(allow_patterns = ["*UD-Q2_K_XL*"]),
        modelscope_model_id="unsloth/DeepSeek-R1-GGUF",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)

Model.register(
    dict(
        model_id = "DeepSeek-R1",
        supported_engines=[vllm_deepseek_r1_engine084],
        supported_instances=[
            local_instance
        ],
        supported_services=[
            local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        allow_china_region=True,
        need_prepare_model=False,
        huggingface_model_id="unsloth/DeepSeek-R1",
        modelscope_model_id="unsloth/DeepSeek-R1",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)

Model.register(
    dict(
        model_id = "deepseek-r1-671b-4bit_gguf",
        supported_engines=[ktransformers_engine],
        supported_instances=[
            g5d24xlarge_instance,
            g5d48xlarge_instance,
            g6d24xlarge_instance,
            g6d48xlarge_instance,
            g6e16xlarge_instance,
            g6e24xlarge_instance,
            g6e48xlarge_instance,
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
        need_prepare_model=False,
        huggingface_model_id="unsloth/DeepSeek-R1-GGUF",
        huggingface_model_download_kwargs = dict(allow_patterns = ["*Q4_K_M*"]),
        modelscope_model_id="unsloth/DeepSeek-R1-GGUF",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs for reasoning",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_REASONING_MODEL
    )
)

Model.register(
    dict(
        model_id = "deepseek-v3-UD-IQ1_M_ollama",
        supported_engines=[ollama_deepseek_r1_qwen2d5_1d5b_engine057],
        supported_instances=[
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
        ollama_model_id="milkey/deepseek-v3-UD:IQ1_M",
        # modelscope_model_id="Qwen/Qwen2.5-14B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of DeepSeek LLMs",
        model_type=ModelType.LLM,
        model_series=DEEPSEEK_V3_SERIES
    )
)
