from backend.backend import OpenAICompitableProxyBackendBase
from emd.utils.logger_utils import get_logger

logger = get_logger(__name__)


class LMdeployBackend(OpenAICompitableProxyBackendBase):
    server_port = "11434"

    def create_proxy_server_start_command(self,model_path):
        serve_command = f'lmdeploy serve api_server --server-port {self.server_port} --model-name={self.model_id} --tp {self.gpu_num} {self.default_cli_args} {self.cli_args} {model_path}'
        if self.environment_variables:
            serve_command = f'{self.environment_variables} && {serve_command}'
        if self.api_key:
            serve_command += f" --api-key {self.api_key}"
        return serve_command

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
