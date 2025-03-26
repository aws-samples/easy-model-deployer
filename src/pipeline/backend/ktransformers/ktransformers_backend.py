from backend.backend import OpenAICompitableProxyBackendBase
from emd.utils.logger_utils import get_logger
import os
import re

logger = get_logger(__name__)

class KTransformersBackend(OpenAICompitableProxyBackendBase):
    server_port = "10002"

    def get_gguf_path(self, folder_path):
        patterns = [r".*UD-IQ1_S.*", r".*UD-Q2_K_XL.*", r".*Q4_K_M.*"]

        regexes = [re.compile(pattern) for pattern in patterns]

        default_subfolder_path = None

        logger.info(f"folder_path: {folder_path}")
        for subfolder_name in os.listdir(folder_path):
            logger.info(f"subfolder_name: {subfolder_name}")
            subfolder_path = os.path.join(folder_path, subfolder_name)
            logger.info(f"subfolder_path: {subfolder_path}")
            if default_subfolder_path is None:
                default_subfolder_path = subfolder_path

            if os.path.isdir(subfolder_path):
                os.system(f'ls -l {subfolder_path}')
                for regex in regexes:
                    if regex.match(subfolder_name):
                        return subfolder_path

        return default_subfolder_path

    def format_devices(self):
        return ",".join([f"CUDA{i}" for i in range(self.gpu_num)])

    def create_proxy_server_start_command(self,model_path):
        # find gguf from model path
        TORCH_CUDA_ARCH_LIST = None
        if 'g5' in self.instance_type:
            TORCH_CUDA_ARCH_LIST = '8.6'
        elif 'g6' in self.instance_type:
            TORCH_CUDA_ARCH_LIST = '8.9'
        else:
            raise ValueError(f"Unsupported instance type!")

        cpu_infer = self.cpu_num - 2
        gguf_path = self.get_gguf_path(model_path)

        serve_command = f'bash -c "source /opt/ml/code/venv/bin/activate && cd /opt/ml/code/ktransformers && chmod +x install.sh && ./install.sh && TORCH_CUDA_ARCH_LIST={TORCH_CUDA_ARCH_LIST} python /opt/ml/code/ktransformers/ktransformers/server/main.py  --model_path /opt/ml/model/DeepSeek-R1  --gguf_path {gguf_path} --port {self.server_port} --cpu_infer {cpu_infer}"'
        if self.environment_variables:
            serve_command = f'{self.environment_variables} && {serve_command}'
        return serve_command

    def invoke(self, request):
        # Transform input to lmdeploy format
        request = self._transform_request(request)
        logger.info(f"Chat request:{request}")
        response = self.client.chat.completions.create(**request)
        logger.info(f"response:{response}")
        if request.get('stream',False):
            return self._transform_streaming_response(response)
        else:
            return self._transform_response(response)
