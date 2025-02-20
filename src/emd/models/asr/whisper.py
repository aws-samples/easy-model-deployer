from .. import Model
from ..engines import huggingface_whisper_engine
from ..services import sagemaker_async_service
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
)
from emd.models.utils.constants import ModelType
from emd.models import ModelSeries

from ..model_series import WHISPER_SERIES
Model.register(
    dict(
        model_id = "whisper",
        supported_engines=[huggingface_whisper_engine],
        supported_instances=[
            g5dxlarge_instance,
            g5d2xlarge_instance,
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            # g5d12xlarge_instance,
            g5d16xlarge_instance,
            # g5d24xlarge_instance,
            # g5d48xlarge_instance,
        ],
        supported_services=[sagemaker_async_service],
        supported_frameworks=[fastapi_framework],
        application_scenario="asr",
        description="The Whisper model is an advanced speech-to-text system developed by OpenAI, capable of transcribing audio in multiple languages with high accuracy. It is designed to handle various audio inputs, including noisy environments, and can also translate spoken language into text.",
        need_prepare_model=False,
        model_type=ModelType.WHISPER,
        model_series=WHISPER_SERIES
    )
)
