import httpx
import sys
import os
from emd.models.utils.constants import ModelType

from backend.backend import OpenAICompitableProxyBackendBase
from emd.utils.logger_utils import get_logger

logger = get_logger(__name__)

class VLLMBackend(OpenAICompitableProxyBackendBase):

    def create_proxy_server_start_command(self,model_path):
        os.system(f"{sys.executable} -m pip list")
        serve_command = f'vllm serve {model_path} --port {self.server_port} --trust-remote-code --served-model-name={self.model_id} --tensor_parallel_size={self.gpu_num} {self.default_cli_args} {self.cli_args}'
        if self.environment_variables:
            serve_command = f'{self.environment_variables} && {serve_command}'

        if self.model_type == ModelType.RERANK:
            serve_command += " --task score"
        if self.api_key:
            serve_command += f" --api-key {self.api_key}"
        return serve_command


    def invoke(self, request):
        # Transform input to vllm format
        request = self._transform_request(request)
        # Invoke vllm
        logger.info(f"Chat request:{request}")
        if self.model_type == ModelType.EMBEDDING:
            # print('cal embedding....')
            response = self.client.embeddings.create(**request)
            # print('end cal embedding....')
        elif self.model_type == ModelType.RERANK:
            headers = {
                "accept": "application/json",
                "Accept-Type": "application/json",
            }
            response = httpx.post(
                f'{self.base_url}/score',
                json=request,
                headers=headers
            ).json()
        else:
            response = self.client.chat.completions.create(**request)
        logger.info(f"response:{response},{request}")

        if request.get("stream", False):
            return self._transform_streaming_response(response)
        else:
            return self._transform_response(response)

    async def ainvoke(self, request):
        # Transform input to vllm format
        request = self._transform_request(request)
        # Invoke vllm
        logger.info(f"Chat request:{request}")
        if self.model_type == ModelType.EMBEDDING:
            # print('cal embedding....')
            response = await self.async_client.embeddings.create(**request)
            # print('end cal embedding....')
        elif self.model_type == ModelType.RERANK:
            headers = {
                "accept": "application/json",
                "Accept-Type": "application/json",
            }
            response = httpx.post(
                f'{self.base_url}/score',
                json=request,
                headers=headers
            ).json()
        else:
            response = await self.async_client.chat.completions.create(**request)
        logger.info(f"response:{response},{request}")

        if request.get("stream", False):
            logger.info(f"engine streaming response {response}")
            return await self._atransform_streaming_response(response)
        else:
            return await self._atransform_response(response)
