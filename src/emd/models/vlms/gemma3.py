from ..engines import vllm_gemma3_engine
from .. import Model
from ..frameworks import fastapi_framework
from ..services import (
    sagemaker_service,
    sagemaker_async_service,
    ecs_service,
    local_service
)
from emd.models.utils.constants import ModelType
from ..model_series import Gemma3_SERIES
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
from ..utils.constants import ModelFilesDownloadSource


Model.register(
    dict(
        model_id = "gemma-3-4b-it",
        supported_engines=[vllm_gemma3_engine],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d16xlarge_instance,
            local_instance
        ],
        supported_services=[
            sagemaker_service, sagemaker_async_service,local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        modelscope_model_id="LLM-Research/gemma-3-4b-it",
        model_files_download_source=ModelFilesDownloadSource.MODELSCOPE,
        # require_huggingface_token=False,
        application_scenario="vision llms for image understanding",
        description="The latest series of Gemma 3",
        model_type=ModelType.VLM,
        model_series=Gemma3_SERIES,
    )
)


Model.register(
    dict(
        model_id = "gemma-3-12b-it",
        supported_engines=[vllm_gemma3_engine],
        supported_instances=[
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g5d16xlarge_instance,
            local_instance
        ],
        supported_services=[
            sagemaker_service, sagemaker_async_service,local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        # huggingface_model_id="google/gemma-3-12b-it",
        # require_huggingface_token=False,
        modelscope_model_id="LLM-Research/gemma-3-12b-it",
        model_files_download_source=ModelFilesDownloadSource.MODELSCOPE,
        application_scenario="vision llms for image understanding",
        description="The latest series of Gemma 3",
        model_type=ModelType.VLM,
        model_series=Gemma3_SERIES,
    )
)


Model.register(
    dict(
        model_id = "gemma-3-27b-it",
        supported_engines=[vllm_gemma3_engine],
        supported_instances=[
            g5d12xlarge_instance,
            g5d24xlarge_instance,
            g5d48xlarge_instance,
            local_instance
        ],
        disable_hf_transfer=True,
        supported_services=[
            sagemaker_service, sagemaker_async_service,local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        # huggingface_model_id="unsloth/gemma-3-27b-it",
        modelscope_model_id="LLM-Research/gemma-3-27b-it",
        model_files_download_source=ModelFilesDownloadSource.MODELSCOPE,
        # require_huggingface_token=False,
        application_scenario="vision llms for image understanding",
        description="The latest series of Gemma 3",
        model_type=ModelType.VLM,
        model_series=Gemma3_SERIES,
    )
)
