from backend.backend import OpenAICompitableProxyBackendBase
from emd.utils.logger_utils import get_logger
import glob
import os
import time
import threading

logger = get_logger(__name__)


class LlamaCppBackend(OpenAICompitableProxyBackendBase):
    server_port = "11434"

    def find_gguf_file(self,model_path):
        if os.path.exists(model_path):
            if model_path.endswith(".gguf"):
                return model_path
            else:
                gghf_file_paths = glob.glob(os.path.join(model_path,"**/*.gguf"),recursive=True)
                if not gghf_file_paths:
                    raise ValueError(f"no gguf file found in {model_path}")

                if  len(gghf_file_paths) == 1:
                    return gghf_file_paths[0]

                first_gguf_file_paths = glob.glob(os.path.join(model_path,"**/*001*.gguf"),recursive=True)
                if not first_gguf_file_paths:
                    raise ValueError(f"no 001 gguf file found in {model_path}, all gguf files: {gghf_file_paths}")
                if len(first_gguf_file_paths) > 1:
                    raise ValueError(f"multiple 001 gguf files found in {model_path}, all gguf files: {gghf_file_paths}")
                return first_gguf_file_paths[0]
        else:
            raise FileNotFoundError(f"model path {model_path} not found")


    def format_devices(self):
        return ",".join([f"CUDA{i}" for i in range(self.gpu_num)])

    def create_proxy_server_start_command(self,model_path):
        # find gguf from model path
        gguf_model_path = self.find_gguf_file(model_path)
        n_gpu_layers = int(0x7FFFFFFF)
        serve_command = f'/llama.cpp/llama-server --n-gpu-layers {n_gpu_layers} -dev {self.format_devices()} {self.default_cli_args} {self.cli_args} --no-webui  --port {self.server_port} -m {gguf_model_path} --alias {self.model_id}'
        if self.environment_variables:
            serve_command = f'{self.environment_variables} && {serve_command}'
        if self.api_key:
            serve_command += f" --api-key {self.api_key}"
        return serve_command

    def check_model_serve_ready(self,thread:threading.Thread,host,port):
        import openai
        while True:
            try:
                for m in self.client.models.list():
                    if self.model_id in m.id:
                        return
                logger.info(f"model: {self.model_id} starting...")
                time.sleep(5)
            except (openai.NotFoundError,openai.InternalServerError,openai.APIConnectionError) as e:
                logger.info(f"model: {self.model_id} error: {str(e)}, starting...")
                time.sleep(5)

    def invoke(self, request):
        # Transform input to lmdeploy format
        request = self._transform_request(request)
        # Invoke lmdeploy
        logger.info(f"Chat request:{request}")
        # if self.model_type == ModelType.EMBEDDING:
        #     # print('cal embedding....')
        #     response = self.client.embeddings.create(**request)
        #     # print('end cal embedding....')
        # elif self.model_type == ModelType.RERANK:
        #     headers = {
        #         "accept": "application/json",
        #         "Accept-Type": "application/json",
        #     }
        #     response = httpx.post(
        #         f'http://localhost:{self.server_port}/v1/score',
        #         json=request,
        #         headers=headers
        #     ).json()
        # else:
        response = self.client.chat.completions.create(**request)
        logger.info(f"response:{response}")
        if request.get('stream',False):
            return self._transform_streaming_response(response)
        else:
            return self._transform_response(response)

    async def ainvoke(self, request):
        # Transform input to lmdeploy format
        request = self._transform_request(request)
        # Invoke lmdeploy
        logger.info(f"Chat request:{request}")
        response = await self.async_client.chat.completions.create(**request)
        logger.info(f"response:{response}")
        if request.get('stream',False):
            return await self._atransform_streaming_response(response)
        else:
            return await self._atransform_response(response)
