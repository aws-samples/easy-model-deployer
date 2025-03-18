from backend.backend import OpenAICompitableProxyBackendBase
from emd.utils.logger_utils import get_logger
from emd.models import Instance
import os
from emd.utils.accelerator_utils import (
    check_cuda_exists,
    check_neuron_exists,
    get_gpu_num,
    get_neuron_core_num
)
from emd.constants import EMD_MODELS_S3_KEY_TEMPLATE

logger = get_logger(__name__)


class TgiBackend(OpenAICompitableProxyBackendBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compile_to_neuron = self.execute_model.executable_config.current_engine.compile_to_neuron
        self.neuron_compile_params = self.execute_model.executable_config.current_engine.neuron_compile_params
        self.entrypoint = self.execute_model.executable_config.current_engine.entrypoint
    def get_shard_num(self):
        if check_cuda_exists():
            return self.gpu_num
        elif check_neuron_exists():
            return self.neuron_core_num
        else:
            raise RuntimeError("No cuda or neuron device found")

    def create_proxy_server_start_command(self,model_path):
        shard_num_cli_args = ""
        if check_cuda_exists():
            shard_num_cli_args = f"--num-shard {self.get_shard_num()}"
        serve_command = f'{self.entrypoint} --trust-remote-code --model-id {model_path} --port {self.server_port} {self.default_cli_args} {shard_num_cli_args} {self.cli_args}'
        if self.environment_variables:
            serve_command = f'{self.environment_variables} && {serve_command}'
        if self.api_key:
            serve_command += f" --api-key {self.api_key}"
        return serve_command

    def convert_model_to_neuron(self,model_path,output_path):
        convert_cmd = "optimum-cli export neuron" \
                      f" --model {model_path}"

        for k,v in self.neuron_compile_params.items():
            convert_cmd += f" --{k} {v}"
        convert_cmd += f" {output_path}"
        logger.info(f"convert cmd: {convert_cmd}")
        assert os.system(convert_cmd) == 0
        return output_path

        # from optimum.neuron import NeuronModelForCausalLM
        # compiler_args = self.neuron_compile_params
        # model = NeuronModelForCausalLM.from_pretrained(
        #         model_path,
        #         export=True,
        #         **compiler_args
        #     )
        # model.save_pretrained(otuput_path)


    def before_start(self,model_dir=None):
        model_abs_path = super().before_start(model_dir=model_dir)
        # model_dir = None
        if self.compile_to_neuron:
            # compile the model to neuron
            # model_dir = os.environ.get("MODEL_DIR") or EMD_MODELS_S3_KEY_TEMPLATE.format(model_id=self.model_id)
            # model_abs_path = os.path.abspath(model_dir)
            output_path = os.path.join(model_abs_path+'_neuron')
            logger.info(f"compiling model to neuron from {model_abs_path} to {output_path}...")
            self.convert_model_to_neuron(
                model_abs_path,
                output_path
            )
            model_abs_path = output_path
            logger.info(f"compile model to neuron done")

        return model_abs_path

        # return super().start(model_dir=model_dir)


    def invoke(self, request):
        # Transform input to tgi format
        request = self._transform_request(request)
        request['model'] = 'tgi'
        # Invoke tgi
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
        # Transform input to tgi format
        request = self._transform_request(request)
        request['model'] = 'tgi'
        # Invoke tgi
        logger.info(f"Chat request:{request}")
        response = await self.async_client.chat.completions.create(**request)
        logger.info(f"response:{response}")
        if request.get('stream',False):
            return await self._atransform_streaming_response(response)
        else:
            return await self._atransform_response(response)
