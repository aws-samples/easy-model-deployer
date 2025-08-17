from .. import Model
from ..model_series import DOTS_OCR_SERIES
from ..engines import vllm_dots_ocr_engine091, huggingface_llm_engine_4d41d2
from ..instances import (
    g5dxlarge_instance,
    g5d2xlarge_instance,
    g5d4xlarge_instance,
    g5d8xlarge_instance,
    local_instance
)
from ..services import (
    sagemaker_service,
    sagemaker_async_service,
    ecs_service,
    local_service
)
from ..frameworks import fastapi_framework
from emd.models.utils.constants import ModelType

Model.register(
    dict(
        model_id="dotsocr",
        model_type=ModelType.VLM,
        description="dots.ocr is a powerful, multilingual document parser that unifies layout detection and content recognition within a single vision-language model. Built on a compact 1.7B-parameter LLM foundation, it achieves state-of-the-art performance on text, tables, and reading order tasks with support for over 100 languages including English, Chinese, and many others.",
        application_scenario="multilingual document layout parsing, OCR, document understanding, table extraction, formula recognition, reading order detection",
        supported_engines=[vllm_dots_ocr_engine091],
        supported_instances=[
            g5dxlarge_instance, g5d2xlarge_instance, g5d4xlarge_instance, g5d8xlarge_instance, local_instance
        ],
        supported_services=[
            sagemaker_service, sagemaker_async_service, ecs_service, local_service
        ],
        supported_frameworks=[
            fastapi_framework
        ],
        allow_china_region=True,
        huggingface_model_id="rednote-hilab/dots.ocr",
        modelscope_model_id="rednote-hilab/dots.ocr",
        require_huggingface_token=False,
        model_series=DOTS_OCR_SERIES,
    )
)
