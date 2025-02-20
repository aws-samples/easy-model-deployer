from .. import Model
from ..utils.constants import ModelType
from ..engines import comfyui_engine
from ..services import sagemaker_service, sagemaker_async_service
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
)
from ..model_series import COMFYUI_SERIES

Model.register(
    dict(
        model_id = "txt2video-LTX",
        supported_engines=[comfyui_engine],
        supported_instances=[
            g5d4xlarge_instance,
            g5d8xlarge_instance,
            g6e2xlarge_instance
        ],
        supported_services=[
            sagemaker_async_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        huggingface_url_list={"https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltx-video-2b-v0.9.1.safetensors": "models/checkpoints",
                              "https://huggingface.co/mcmonkey/google_t5-v1_1-xxl_encoderonly/resolve/main/t5xxl_fp8_e4m3fn.safetensors": "models/clip"},
        huggingface_model_list=None,
        require_huggingface_token=False,
        application_scenario="txt to image and image to video",
        description="video generation with LTX model,LTX-Video can generate high-quality videos in real-time. It can generate 24 FPS videos at 768x512 resolution",
        model_type=ModelType.VIDEO,
        model_series=COMFYUI_SERIES
    )
)
