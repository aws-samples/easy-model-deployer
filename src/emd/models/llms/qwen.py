from .. import Model
from ..engines import (
    vllm_qwen2d5_engine064,
    vllm_qwen2d5_128k_engine064,
    huggingface_llm_engine_4d41d2,
    tgi_qwen2d5_72b_engine064,
    tgi_qwen2d5_on_inf2,
    tgi_qwen2d5_72b_on_inf2,
    vllm_qwen2d5_72b_engine064,
    vllm_qwq_engine073
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
    g4dn2xlarge_instance,
    g6e2xlarge_instance,
    inf2d8xlarge_instance,
    inf2d24xlarge_instance,
    local_instance
)
from emd.models.utils.constants import ModelType
from emd.models.utils.constants import ModelType
from emd.models import ModelSeries
from ..model_series import QWEN2D5_SERIES,QWEN_REASONING_MODEL

Model.register(
    dict(
        model_id = "Qwen2.5-7B-Instruct",
        supported_engines=[
            vllm_qwen2d5_engine064,
            tgi_qwen2d5_72b_engine064,
            tgi_qwen2d5_on_inf2
        ],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d12xlarge_instance,
            g5d16xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
            inf2d8xlarge_instance,
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
        huggingface_model_id="Qwen/Qwen2.5-7B-Instruct",
        modelscope_model_id="Qwen/Qwen2.5-7B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of Qwen LLMs, offers base and tuned models from 0.5B to 72B\n parameters, featuring enhanced knowledge, improved coding and math skills, better instruction\n following, long-text generation, structured data handling, 128K token context support, and\n multilingual capabilities for 29+ languages.",
        model_type=ModelType.LLM,
        model_series=QWEN2D5_SERIES
    )
)


Model.register(
    dict(
        model_id = "Qwen2.5-72B-Instruct-AWQ",
        supported_engines=[
            vllm_qwen2d5_engine064,
            tgi_qwen2d5_72b_engine064
        ],
        supported_instances=[
            g5d12xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
            inf2d24xlarge_instance,
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
        huggingface_model_id="Qwen/Qwen2.5-72B-Instruct-AWQ",
        modelscope_model_id="Qwen/Qwen2.5-72B-Instruct-AWQ",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of Qwen LLMs, offers base and tuned models from 0.5B to 72B\n parameters, featuring enhanced knowledge, improved coding and math skills, better instruction\n following, long-text generation, structured data handling, 128K token context support, and\n multilingual capabilities for 29+ languages.",
        model_type=ModelType.LLM,
        model_series=QWEN2D5_SERIES
    )
)

# Model.register(
#     dict(
#         model_id = "Qwen2.5-72B-Instruct-AWQ-inf2",
#         supported_engines=[
#             tgi_qwen2d5_72b_on_inf2
#         ],
#         supported_instances=[
#             inf2d24xlarge_instance,
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
#         allow_china_region=True,
#         huggingface_model_id="Qwen/Qwen2.5-72B-Instruct-AWQ",
#         modelscope_model_id="Qwen/Qwen2.5-72B-Instruct-AWQ",
#         require_huggingface_token=False,
#         application_scenario="Agent, tool use, translation, summary",
#         description="The latest series of Qwen LLMs, offers base and tuned models from 0.5B to 72B\n parameters, featuring enhanced knowledge, improved coding and math skills, better instruction\n following, long-text generation, structured data handling, 128K token context support, and\n multilingual capabilities for 29+ languages.",
#         model_type=ModelType.LLM,
#         model_series=QWEN2D5_SERIES
#     )
# )


Model.register(
    dict(
        model_id = "Qwen2.5-72B-Instruct",
        supported_engines=[
            vllm_qwen2d5_72b_engine064,
            # tgi_qwen2d5_72b_engine064
        ],
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
        allow_china_region=True,
        huggingface_model_id="Qwen/Qwen2.5-72B-Instruct",
        modelscope_model_id="Qwen/Qwen2.5-72B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of Qwen LLMs, offers base and tuned models from 0.5B to 72B\n parameters, featuring enhanced knowledge, improved coding and math skills, better instruction\n following, long-text generation, structured data handling, 128K token context support, and\n multilingual capabilities for 29+ languages.",
        model_type=ModelType.LLM,
        need_prepare_model=False,
        model_series=QWEN2D5_SERIES
    )
)

Model.register(
    dict(
        model_id = "Qwen2.5-72B-Instruct-AWQ-128k",
        supported_engines=[vllm_qwen2d5_128k_engine064],
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
        huggingface_model_id="Qwen/Qwen2.5-72B-Instruct-AWQ",
        modelscope_model_id="Qwen/Qwen2.5-72B-Instruct-AWQ",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of Qwen LLMs, offers base and tuned models from 0.5B to 72B\n parameters, featuring enhanced knowledge, improved coding and math skills, better instruction\n following, long-text generation, structured data handling, 128K token context support, and\n multilingual capabilities for 29+ languages.",
        model_type=ModelType.LLM,
        model_series=QWEN2D5_SERIES
    )
)

Model.register(
    dict(
        model_id = "Qwen2.5-32B-Instruct",
        supported_engines=[vllm_qwen2d5_engine064],
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
        huggingface_model_id="Qwen/Qwen2.5-32B-Instruct",
        modelscope_model_id="Qwen/Qwen2.5-32B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of Qwen LLMs, offers base and tuned models from 0.5B to 72B\n parameters, featuring enhanced knowledge, improved coding and math skills, better instruction\n following, long-text generation, structured data handling, 128K token context support, and\n multilingual capabilities for 29+ languages.",
        model_type=ModelType.LLM,
        model_series=QWEN2D5_SERIES
    )
)

# Model.register(
#     dict(
#         model_id = "Qwen2.5-32B-Instruct-inf2",
#         supported_engines=[tgi_qwen2d5_72b_on_inf2],
#         supported_instances=[
#             inf2d24xlarge_instance,
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
#         allow_china_region=True,
#         huggingface_model_id="Qwen/Qwen2.5-32B-Instruct",
#         modelscope_model_id="Qwen/Qwen2.5-32B-Instruct",
#         require_huggingface_token=False,
#         application_scenario="Agent, tool use, translation, summary",
#         description="The latest series of Qwen LLMs, offers base and tuned models from 0.5B to 72B\n parameters, featuring enhanced knowledge, improved coding and math skills, better instruction\n following, long-text generation, structured data handling, 128K token context support, and\n multilingual capabilities for 29+ languages.",
#         model_type=ModelType.LLM,
#         model_series=QWEN2D5_SERIES
#     )
# )

Model.register(
    dict(
        model_id = "Qwen2.5-0.5B-Instruct",
        supported_engines=[
            vllm_qwen2d5_engine064,
            tgi_qwen2d5_on_inf2
            ],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            # g5d12xlarge_instance,
            g5d16xlarge_instance,
            # g5d24xlarge_instance,
            # g5d48xlarge_instance,
            inf2d8xlarge_instance,
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
        huggingface_model_id="Qwen/Qwen2.5-0.5B-Instruct",
        modelscope_model_id="Qwen/Qwen2.5-0.5B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of Qwen LLMs, offers base and tuned models from 0.5B to 72B\n parameters, featuring enhanced knowledge, improved coding and math skills, better instruction\n following, long-text generation, structured data handling, 128K token context support, and\n multilingual capabilities for 29+ languages.",
        model_type=ModelType.LLM,
        model_series=QWEN2D5_SERIES,
    )
)



Model.register(
    dict(
        model_id = "Qwen2.5-1.5B-Instruct",
        supported_engines=[vllm_qwen2d5_engine064],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            # g5d12xlarge_instance,
            g5d16xlarge_instance,
            # g5d24xlarge_instance,
            # g5d48xlarge_instance,
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
        huggingface_model_id="Qwen/Qwen2.5-1.5B-Instruct",
        modelscope_model_id="Qwen/Qwen2.5-1.5B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of Qwen LLMs, offers base and tuned models from 0.5B to 72B\n parameters, featuring enhanced knowledge, improved coding and math skills, better instruction\n following, long-text generation, structured data handling, 128K token context support, and\n multilingual capabilities for 29+ languages.",
        model_type=ModelType.LLM,
        model_series=QWEN2D5_SERIES
    )
)


Model.register(
    dict(
        model_id = "Qwen2.5-3B-Instruct",
        supported_engines=[vllm_qwen2d5_engine064],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            # g5d12xlarge_instance,
            g5d16xlarge_instance,
            # g5d24xlarge_instance,
            # g5d48xlarge_instance,
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
        huggingface_model_id="Qwen/Qwen2.5-3B-Instruct",
        modelscoope_model_id="Qwen/Qwen2.5-3B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of Qwen LLMs, offers base and tuned models from 0.5B to 72B\n parameters, featuring enhanced knowledge, improved coding and math skills, better instruction\n following, long-text generation, structured data handling, 128K token context support, and\n multilingual capabilities for 29+ languages.",
        model_type=ModelType.LLM,
        model_series=QWEN2D5_SERIES
    )
)


Model.register(
    dict(
        model_id = "Qwen2.5-14B-Instruct-AWQ",
        supported_engines=[vllm_qwen2d5_engine064],
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
        huggingface_model_id="Qwen/Qwen2.5-14B-Instruct-AWQ",
        modelscope_model_id="Qwen/Qwen2.5-14B-Instruct-AWQ",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of Qwen LLMs, offers base and tuned models from 0.5B to 72B\n parameters, featuring enhanced knowledge, improved coding and math skills, better instruction\n following, long-text generation, structured data handling, 128K token context support, and\n multilingual capabilities for 29+ languages.",
        model_type=ModelType.LLM,
        model_series=QWEN2D5_SERIES
    )
)


Model.register(
    dict(
        model_id = "Qwen2.5-14B-Instruct",
        supported_engines=[vllm_qwen2d5_engine064],
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
        huggingface_model_id="Qwen/Qwen2.5-14B-Instruct",
        modelscope_model_id="Qwen/Qwen2.5-14B-Instruct",
        require_huggingface_token=False,
        application_scenario="Agent, tool use, translation, summary",
        description="The latest series of Qwen LLMs, offers base and tuned models from 0.5B to 72B\n parameters, featuring enhanced knowledge, improved coding and math skills, better instruction\n following, long-text generation, structured data handling, 128K token context support, and\n multilingual capabilities for 29+ languages.",
        model_type=ModelType.LLM,
        model_series=QWEN2D5_SERIES
    )
)


Model.register(
    dict(
        model_id = "QwQ-32B-Preview",
        supported_engines=[vllm_qwq_engine073],
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
        huggingface_model_id="Qwen/QwQ-32B-Preview",
        modelscope_model_id="Qwen/QwQ-32B-Preview",
        require_huggingface_token=False,
        application_scenario="large reasoning model",
        description="large reasoning model provide by qwen team",
        model_type=ModelType.LLM,
        model_series=QWEN_REASONING_MODEL
    )
)

Model.register(
    dict(
        model_id = "QwQ-32B",
        supported_engines=[vllm_qwq_engine073],
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
        huggingface_model_id="Qwen/QwQ-32B",
        modelscope_model_id="Qwen/QwQ-32B",
        require_huggingface_token=False,
        application_scenario="large reasoning model",
        description="large reasoning model provide by qwen team",
        model_type=ModelType.LLM,
        model_series=QWEN_REASONING_MODEL
    )
)
