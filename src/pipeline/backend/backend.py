from abc import ABC, abstractmethod
from typing import Iterable, List
from emd.models import Model,Engine
from typing import Iterable, List
import os
import time
import logging
import subprocess
import signal
import traceback
import json
import socket
import threading
from fastapi.concurrency import run_in_threadpool


# import httpx
from emd.models.utils.constants import ModelType,ServiceType
from emd.models import Engine
from emd.utils.accelerator_utils import get_gpu_num,get_neuron_core_num


from utils.common import download_dir_from_s3_by_s5cmd
# import torch
from emd.constants import EMD_MODELS_S3_KEY_TEMPLATE
from emd.utils.logger_utils import get_logger

logger = get_logger(__name__)

class BackendBase(ABC):
    def __init__(self,model:Model):
        self.execute_model: Model = model

    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def invoke(self, request):
        ...

    async def ainvoke(self, request):
        return await run_in_threadpool(self.invoke, request)


class OpenAICompitableProxyBackendBase(BackendBase):
    server_port = "8000"

    @property
    def base_url(self):
        return f"http://localhost:{self.server_port}/v1"


    def __init__(self,*args,**kwargs):
        super().__init__(
              *args,
              **kwargs
        )
        from openai import OpenAI, AsyncOpenAI
        self.client = OpenAI(
            base_url=self.base_url,
            api_key="NOT SET"
        )
        self.async_client = AsyncOpenAI(
            base_url=self.base_url,
            api_key="NOT SET"
        )
        self.model_id = self.execute_model.model_id
        self.model_s3_bucket = self.execute_model.executable_config.model_s3_bucket
        self.model_files_s3_path = self.execute_model.model_files_s3_path
        self.service_type = self.execute_model.executable_config.current_service.service_type
        self.instance_type = self.execute_model.executable_config.current_instance.instance_type
        self.api_key = self.execute_model.executable_config.current_engine.api_key
        self.cli_args = self.execute_model.executable_config.current_engine.cli_args
        self.default_cli_args = self.execute_model.executable_config.current_engine.default_cli_args
        self.custom_gpu_num = self.execute_model.executable_config.current_engine.custom_gpu_num
        self.custom_neuron_core_num = self.execute_model.executable_config.current_engine.custom_neuron_core_num
        self.environment_variables = self.execute_model.executable_config.current_engine.environment_variables
        self.engine_type = self.execute_model.executable_config.current_engine.engine_type
        # self.gpu_num = torch.cuda.device_count()
        self.model_type = self.execute_model.model_type
        self.proc = None


    @property
    def gpu_num(self):
        if self.custom_gpu_num is not None:
            return self.custom_gpu_num
        return get_gpu_num()

    @property
    def neuron_core_num(self):
        if self.custom_neuron_core_num is not None:
            return self.custom_neuron_core_num
        return get_neuron_core_num()

    def create_proxy_server_start_command(self,model_path):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def wait_until_server_start(self,thread:threading.Thread,host,port):

        def check_server_status(host, port):
            try:
                # 创建一个 socket 对象
                sock = socket.create_connection((host, port), timeout=5)
                sock.close()
                logger.info(f"server {host}:{port} ready.")
                return True
            except (socket.timeout, ConnectionRefusedError):
                logger.info(f"server {host}:{port} starting...")
            except Exception as e:
                logger.info(f"error：{str(e)}")
            return False

        while True:
            if check_server_status(host,port):
                break
            if not thread.is_alive():
                raise RuntimeError('openai server failed to start.')
            time.sleep(5)

    def check_model_serve_ready(self,thread:threading.Thread,host,port):
        self.wait_until_server_start(
            thread,
            host,
            port
        )

    def start_server(self, server_start_command):
        logger.info(f"Starting {self.engine_type} server with command: {server_start_command}")
        t = threading.Thread(target=os.system,args=(server_start_command,),daemon=True)
        t.start()
        self.check_model_serve_ready(
            t,
            "127.0.0.1",
            self.server_port
        )
        return


    def download_model_files(self,model_dir):
        from deploy.prepare_model import download_model_files as _download_model_files
        _download_model_files(self.execute_model,model_dir)


    def before_start(self,model_dir=None):
        if model_dir is None:
            model_dir = os.environ.get("MODEL_DIR") or EMD_MODELS_S3_KEY_TEMPLATE.format(model_id=self.model_id)
        model_abs_path = os.path.abspath(model_dir)
        model_files_modify_hook = self.execute_model.executable_config.current_engine.model_files_modify_hook
        model_files_modify_hook_kwargs = self.execute_model.executable_config.current_engine.model_files_modify_hook_kwargs or {}

        if self.service_type != ServiceType.LOCAL:
            if self.execute_model.need_prepare_model or self.model_files_s3_path:
                logger.info(f"Downloading model from s3, model_dir: {model_dir}, bucket_name: {self.model_s3_bucket}")
                download_dir_from_s3_by_s5cmd(
                    model_dir,
                    bucket_name = self.model_s3_bucket,
                    s3_key = model_dir,
                    model_files_s3_path=self.model_files_s3_path
                )
            else:
                logger.info(f"Downloading model from hubs...")
                self.download_model_files(model_dir)

        if model_files_modify_hook:
            logger.info(f"Applying model files modify hook: {model_files_modify_hook}")
            Engine.load_model_files_modify_hook(model_files_modify_hook)(
                model_abs_path,
                **model_files_modify_hook_kwargs
            )
        return model_abs_path


    def start(self,model_dir=None):
        model_abs_path = self.before_start(model_dir=model_dir)

        # get server start command
        server_start_command = self.create_proxy_server_start_command(model_abs_path)
        self.start_server(server_start_command)


    def stop(self):
        if self.proc:
            logger.info(f"pid: {self.proc.pid}")
            logger.info(f"Kill vLLM server")
            logger.info(f"pgid: {os.getpgid(self.proc.pid)}")
            subprocess.Popen(f"kill -9 -{self.proc.pid}", shell=True)
        return


    def _transform_request(self, request):
        # Transform request to docker format
        request['model'] = request.pop('model',self.model_id) or self.model_id
        return request

    def _transform_response(self, response):
        # Transform response to sagemaker format
        return self._get_response(response)

    async def _atransform_response(self, response):
        # Transform response to sagemaker format
        return self._aget_response(response)

    def _transform_streaming_response(self, response):
        # Transform response to sagemaker format
        return self._get_streaming_response(response)

    async def _atransform_streaming_response(self, response):
        # Transform response to sagemaker format
        return self._aget_streaming_response(response)

    def _format_streaming_response(self, response:bytes):
        if self.service_type == ServiceType.SAGEMAKER:
            return response +  "\n"
        else:
            logger.info(f"data: {response}")
            return f"data: {response}\n\n"

    def _get_streaming_response(self, response) -> Iterable[List[str]]:
        try:
            for chunk in response:
                # logger.info(f"chunk: {chunk}")
                yield self._format_streaming_response(chunk.model_dump_json())
        except Exception as e:
            logger.error(traceback.format_exc())
            yield self._format_streaming_response(json.dumps({"error": str(e)}))

    async def _aget_streaming_response(self, response) -> Iterable[List[str]]:
        try:
            async for chunk in response:
                logger.info(f"chunk: {chunk}")
                yield self._format_streaming_response(chunk.model_dump_json())
        except Exception as e:
            logger.error(traceback.format_exc())
            yield self._format_streaming_response(json.dumps({"error": str(e)}))

    async def _aget_response(self, response) -> List[str]:
        return response
