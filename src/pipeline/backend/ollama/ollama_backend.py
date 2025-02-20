from backend.backend import OpenAICompitableProxyBackendBase
from emd.utils.logger_utils import get_logger
import os
import threading
from emd.constants import EMD_MODELS_S3_KEY_TEMPLATE
from emd.models.utils.constants import ModelType,ServiceType
from emd.utils.system_call_utils import execute_command
import time
import traceback

logger = get_logger(__name__)

class OllamaBackend(OpenAICompitableProxyBackendBase):
    server_port = "11434"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.ollama_serve_extra_cli_args = self.execute_model.executable_config.current_engine.ollama_serve_extra_cli_args
        self.ollama_model_id = self.execute_model.ollama_model_id

    def run_ollama_serve(self,model_dir):
        serve_args = f'export OLLAMA_FLASH_ATTENTION=1 {self.default_cli_args} && export OLLAMA_HOST=0.0.0.0:{self.server_port} && export OLLAMA_KEEP_ALIVE=-1 && export OLLAMA_MODELS="{model_dir}" && ollama serve'
        logger.info(f'start ollama serve, args: {serve_args}...')
        t = threading.Thread(target=os.system,args=(serve_args,),daemon=True)
        t.start()
        self.wait_until_server_start(
            t,
            "127.0.0.1",
            self.server_port
        )


    def before_start(self,model_dir=None):
        if model_dir is None:
            model_dir = EMD_MODELS_S3_KEY_TEMPLATE.format(model_id=self.model_id)
        model_abs_path = os.path.abspath(model_dir)
        return model_abs_path

    def create_proxy_server_start_command(self,model_path):
        self.run_ollama_serve(model_path)

        serve_command = f'ollama run {self.ollama_model_id}'
        if self.environment_variables:
            serve_command = f'{self.environment_variables} && {serve_command}'
        # if self.api_key:
        #     serve_command += f" --api-key {self.api_key}"
        return serve_command


    def check_model_serve_ready(self,thread:threading.Thread,host,port):
        import openai
        while True:
            try:
                for m in self.client.models.list():
                    if self.ollama_model_id in m.id:
                        return
                logger.info(f"model: {self.ollama_model_id} starting...")
                time.sleep(5)
            except openai.NotFoundError as e:
                logger.info(f"model: {self.ollama_model_id} error: {str(e)}, starting...")
                time.sleep(5)


    def _transform_request(self, request):
        # Transform request to docker format
        request['model'] = self.ollama_model_id
        return request


    def invoke(self, request):
        # Transform input to lmdeploy format
        request = self._transform_request(request)
        # Invoke ollama server
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
