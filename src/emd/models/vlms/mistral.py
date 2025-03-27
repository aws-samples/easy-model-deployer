from ..engines import vllm_mistral_small_engine082
from .. import Model
from ..frameworks import fastapi_framework
from ..services import (
    sagemaker_service,
    sagemaker_async_service,
    ecs_service,
    local_service
)
from emd.models.utils.constants import ModelType
from ..model_series import MISTRAL_SERIES
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
        model_id = "Mistral-Small-3.1-24B-Instruct-2503",
        supported_engines=[vllm_mistral_small_engine082],
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
        huggingface_model_id="unsloth/Mistral-Small-3.1-24B-Instruct-2503",
        # require_huggingface_token=False,
        modelscope_model_id="mistralai/Mistral-Small-3.1-24B-Instruct-2503",
        # model_files_download_source=ModelFilesDownloadSource.MODELSCOPE,
        application_scenario="vision llms for image understanding",
        description="The latest series of mistral small",
        model_type=ModelType.VLM,
        model_series=MISTRAL_SERIES,
    )
)
