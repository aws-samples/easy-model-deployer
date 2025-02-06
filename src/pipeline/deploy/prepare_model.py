import os
import subprocess
import logging

from huggingface_hub import snapshot_download as hf_snapshot_download
from modelscope import snapshot_download as ms_snapshot_download
from dmaa.models import Model
from dmaa.models.utils.constants import ServiceType,EngineType
from dmaa.utils.aws_service_utils import check_cn_region
from dmaa.utils.logger_utils import get_logger
from utils.common import upload_dir_to_s3_by_s5cmd
from dmaa.constants import DMAA_MODELS_LOCAL_DIR_TEMPLATE,DMAA_MODELS_S3_KEY_TEMPLATE

logger = get_logger(__name__)

def download_huggingface_model(model,args:dict):
    huggingface_model_id = model.huggingface_model_id
    service_type = model.executable_config.current_service.service_type
    model_id = model.model_id
    model_dir = DMAA_MODELS_LOCAL_DIR_TEMPLATE.format(model_id=model_id)
    # os.environ['HF_ENDPOINT'] = huggingface_endpoint
    # export HF_ENDPOINT=https://hf-mirror.com
    hf_endpoint_from_cli = args.get("model_params",{}).get("hf_endpoint")
    huggingface_endpoint = model.huggingface_endpoint
    huggingface_endpoint = hf_endpoint_from_cli or huggingface_endpoint
    os.environ['HF_ENDPOINT'] = huggingface_endpoint
    logger.info(f"Downloading {huggingface_model_id} model from endpoint: {huggingface_endpoint}")

    hf_snapshot_download(
        huggingface_model_id, 
        local_dir=model_dir,
        # endpoint=huggingface_endpoint
    )

def download_modelscope_model(model,args=None):
    modelscope_model_id = model.modelscope_model_id
    service_type = model.executable_config.current_service.service_type
    model_id = model.model_id
    model_dir = DMAA_MODELS_LOCAL_DIR_TEMPLATE.format(model_id=model_id)
    logger.info(f"Downloading {modelscope_model_id} model")
    
    ms_snapshot_download(
        model_id=modelscope_model_id, 
        local_dir=model_dir
    )

def download_comfyui_model(model,args=None):
    model_id = model.model_id
    huggingface_model_list = model.huggingface_model_list
    huggingface_url_list = model.huggingface_url_list
    model_dir = DMAA_MODELS_LOCAL_DIR_TEMPLATE.format(model_id=model_id)
    os.makedirs(model_dir, exist_ok=True)
    if huggingface_model_list is not None:
        for key, value in huggingface_model_list.items():
            logger.info(f"Downloading {key} model")
            huggingface_model_id = key
            model_local_dir = os.path.join(model_dir, value)
            os.makedirs(model_local_dir, exist_ok=True)
            hf_snapshot_download(repo_id=huggingface_model_id, local_dir=model_local_dir)
    if huggingface_url_list is not None:
        for key, value in huggingface_url_list.items():
            logger.info(f"Downloading {os.path.basename(key)} model")
            huggingface_model_url = key
            model_local_dir = os.path.join(model_dir, value)
            os.makedirs(model_local_dir, exist_ok=True)
            subprocess.run(["wget", "-P", model_local_dir, huggingface_model_url])

def upload_model_to_s3(model:Model, model_s3_bucket):
    model_id = model.model_id
    model_dir =  DMAA_MODELS_S3_KEY_TEMPLATE.format(model_id=model_id)  #f"dmaa_models/{model_id}"
    logger.info(f"Uploading {model_id} model to S3")
    upload_dir_to_s3_by_s5cmd(model_s3_bucket, model_dir)

def run(model, model_s3_bucket, backend_type, service_type, region,args):
    if backend_type == EngineType.COMFYUI:
        download_comfyui_model(model,args)
    else:
        if check_cn_region(region):
            download_modelscope_model(model,args)
        else:
            download_huggingface_model(model,args)
    if service_type != ServiceType.LOCAL:
        upload_model_to_s3(model, model_s3_bucket)