import os
import subprocess
import logging

from huggingface_hub import snapshot_download as hf_snapshot_download
from modelscope import snapshot_download as ms_snapshot_download
from emd.models import Model
from emd.models.utils.constants import ServiceType,EngineType,ModelFilesDownloadSource
from emd.utils.aws_service_utils import check_cn_region
from emd.utils.logger_utils import get_logger
from utils.common import upload_dir_to_s3_by_s5cmd,download_dir_from_s3_by_s5cmd
from emd.constants import EMD_MODELS_LOCAL_DIR_TEMPLATE,EMD_MODELS_S3_KEY_TEMPLATE
from emd.utils.network_check import check_website_urllib

logger = get_logger(__name__)


def enable_hf_transfer():
    try:
        import hf_transfer
        os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
        from huggingface_hub import constants
        constants.HF_HUB_ENABLE_HF_TRANSFER = True
        logger.info("hf_transfer enabled")
    except ModuleNotFoundError as e:
        logger.info(f"hf_transfer not installed, skip enabling hf_transfer, error: {e}")


def download_huggingface_model(model:Model,model_dir=None):
    if not model.disable_hf_transfer:
        enable_hf_transfer()
    huggingface_model_id = model.huggingface_model_id
    service_type = model.executable_config.current_service.service_type
    model_id = model.model_id
    model_dir = model_dir or EMD_MODELS_LOCAL_DIR_TEMPLATE.format(model_id=model_id)
    # hf_endpoint_from_cli = args.get("model_params",{}).get("hf_endpoint")
    huggingface_endpoints = model.huggingface_endpoints

    if isinstance(huggingface_endpoints,str):
        huggingface_endpoints = [huggingface_endpoints]

    is_download_success = False
    logger.info(f'huggingface_endpoints: {huggingface_endpoints}')
    for huggingface_endpoint in huggingface_endpoints:
        try:
            logger.info(f"Downloading {huggingface_model_id} model from endpoint: {huggingface_endpoint}")
            # check endpoint reacheable
            if not check_website_urllib(huggingface_endpoint):
                logger.error(f"Endpoint {huggingface_endpoint} is not reachable")
                continue
            logger.info(f"model_dir: {model_dir}")
            logger.info(f"model_download_kwarg: {model.huggingface_model_download_kwargs}")
            hf_snapshot_download(
                huggingface_model_id,
                local_dir=model_dir,
                endpoint=huggingface_endpoint,
                **model.huggingface_model_download_kwargs
            )
            is_download_success = True
            break
        except Exception as e:
            logger.error(f"Error downloading {huggingface_model_id} model from endpoint: {huggingface_endpoint}, error: {e}")
            continue

    if not is_download_success:
        raise Exception(f"Failed to download {huggingface_model_id} model from all endpoints: {huggingface_endpoints}")


def download_modelscope_model(model:Model,model_dir=None):
    modelscope_model_id = model.modelscope_model_id
    service_type = model.executable_config.current_service.service_type
    model_id = model.model_id
    model_dir = model_dir or EMD_MODELS_LOCAL_DIR_TEMPLATE.format(model_id=model_id)
    logger.info(f"Downloading {str(modelscope_model_id)} model")

    ms_snapshot_download(
        model_id=modelscope_model_id,
        local_dir=model_dir
    )

def download_comfyui_model(model,model_dir=None):
    model_id = model.model_id
    huggingface_model_list = model.huggingface_model_list
    huggingface_url_list = model.huggingface_url_list
    model_dir = model_dir or EMD_MODELS_LOCAL_DIR_TEMPLATE.format(model_id=model_id)
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
    model_dir =  EMD_MODELS_S3_KEY_TEMPLATE.format(model_id=model_id)  #f"emd_models/{model_id}"
    logger.info(f"Uploading {model_id} model to S3")
    upload_dir_to_s3_by_s5cmd(model_s3_bucket, model_dir)


def download_model_files(model:Model,model_dir=None):
    engine_type = model.executable_config.current_engine.engine_type
    region = model.executable_config.region
    if engine_type == EngineType.COMFYUI:
        download_comfyui_model(model,model_dir=model_dir)
    else:
        if model.model_files_download_source == ModelFilesDownloadSource.AUTO:
            if check_cn_region(region):
                try:
                    download_modelscope_model(model,model_dir=model_dir)
                except Exception as e:
                    logger.error(f"Error downloading {model.model_id} model from modelscope, error: {e}")
                    logger.info("download from huggingface...")
                    download_huggingface_model(model, model_dir=model_dir)
            else:
                download_huggingface_model(model,model_dir=model_dir)
        else:
            if model.model_files_download_source == ModelFilesDownloadSource.HUGGINGFACE:
                download_huggingface_model(model, model_dir=model_dir)
            elif model.model_files_download_source == ModelFilesDownloadSource.MODELSCOPE:
                download_modelscope_model(model, model_dir=model_dir)
            else:
                raise ValueError(f"Invalid model_files_download_source: {model.model_files_download_source}")


def run(model:Model):#, model_s3_bucket, backend_type, service_type, region,args):
    need_prepare_model = model.need_prepare_model
    model_files_s3_path = model.model_files_s3_path
    service_type = model.executable_config.current_service.service_type
    engine_type = model.executable_config.current_engine.engine_type
    model_s3_bucket = model.executable_config.model_s3_bucket
    logger.info(f"need_prepare_model: {need_prepare_model}, model_files_s3_path: {model_files_s3_path}, service_type: {service_type}, engine_type: {engine_type}, model_s3_bucket: {model_s3_bucket}")
    # if  args.service_type == ServiceType.LOCAL or (args.model.need_prepare_model and not args.skip_prepare_model):
    if service_type == ServiceType.LOCAL or (need_prepare_model and model_files_s3_path is None):
        if engine_type == EngineType.OLLAMA:
            logger.info(f"Model {model.model_id} is ollama model, skip prepare model step. need_prepare_model:{need_prepare_model}, model_files_s3_path: {model_files_s3_path}")
            return
        if not need_prepare_model and service_type == ServiceType.LOCAL:
            logger.info("Force to download model when deploy in local")

        if  model.model_files_local_path is not None:
            if service_type == ServiceType.LOCAL:
                logger.info(f"Model {model.model_id} already prepared in local, skip prepare model step. need_prepare_model:{need_prepare_model}, model_files_local_path: {model.model_files_local_path}")
                return
        if model_files_s3_path is not None and service_type == ServiceType.LOCAL:
            # donwload model files from s3 to local
            model_dir = EMD_MODELS_LOCAL_DIR_TEMPLATE.format(model_id=model.model_id)
            os.makedirs(model_dir, exist_ok=True)
            download_dir_from_s3_by_s5cmd(
                local_dir=model_dir,
                model_files_s3_path=model_files_s3_path
            )
            return
        download_model_files(model)
    else:
        logger.info(f"Model {model.model_id} already prepared, skip prepare model step. need_prepare_model:{need_prepare_model}, model_files_s3_path: {model_files_s3_path}")

    if service_type != ServiceType.LOCAL and need_prepare_model:
        upload_model_to_s3(model, model_s3_bucket)
