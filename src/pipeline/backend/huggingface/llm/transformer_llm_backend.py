from typing import Iterable, List
import os
import time

from emd.models.utils.constants import ModelType,ServiceType

from backend.backend import BackendBase
from utils.common import download_dir_from_s3_by_s5cmd
import torch
from emd.constants import EMD_MODELS_LOCAL_DIR_TEMPLATE
from emd.utils.logger_utils import get_logger
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import TextIteratorStreamer
from threading import Thread
import json


logger = get_logger(__name__)


class TransformerLLMBackend(BackendBase):
    def __init__(self,*args,**kwargs):
        super().__init__(
              *args,
              **kwargs
        )
        self.model_id = self.execute_model.model_id
        self.model_s3_bucket = self.execute_model.executable_config.model_s3_bucket
        self.model_files_s3_path = self.execute_model.model_files_s3_path
        self.service_type = self.execute_model.executable_config.current_service.service_type
        self.gpu_num = torch.cuda.device_count()
        self.model_type = self.execute_model.model_type
        self.proc = None
        self.model = None
        self.tokenizer = None
        self.pretrained_model_init_kwargs = self.execute_model.executable_config.current_engine.pretrained_model_init_kwargs or {}
        self.pretrained_tokenizer_init_kwargs = self.execute_model.executable_config.current_engine.pretrained_tokenizer_init_kwargs or {}


    def start(self):
        model_dir = os.environ.get("MODEL_DIR") or EMD_MODELS_LOCAL_DIR_TEMPLATE.format(model_id=self.model_id)
        if self.service_type != ServiceType.LOCAL:
            logger.info(f"Downloading model from s3")
            download_dir_from_s3_by_s5cmd(
                local_dir=model_dir,
                bucket_name = self.model_s3_bucket,
                s3_key = model_dir,
                model_files_s3_path=self.model_files_s3_path
            )
        model_abs_path = os.path.abspath(model_dir)

        # TODO add model init args from model's definition
        self.model = AutoModelForCausalLM.from_pretrained(
                model_abs_path,
                torch_dtype="auto",
                device_map="auto",
                **self.pretrained_model_init_kwargs


        )
        # TODO add tokenizer init args from model's definition
        self.tokenizer =  AutoTokenizer.from_pretrained(
            model_abs_path,
            **self.pretrained_tokenizer_init_kwargs
        )


    def format_response_as_openai(self,response:str):
        return {
            # "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": time.time(),
            "model": self.model_id,
            # "system_fingerprint": "fp_44709d6fcb",
            "choices": [{
                "index": 0,
                "message": {
                "role": "assistant",
                "content": response,
                },
                "logprobs": None,
                "finish_reason": "stop"
            }],
            # "service_tier": "default",
            # "usage": {
            #     "prompt_tokens": 9,
            #     "completion_tokens": 12,
            #     "total_tokens": 21,
            #     "completion_tokens_details": {
            #     "reasoning_tokens": 0,
            #     "accepted_prediction_tokens": 0,
            #     "rejected_prediction_tokens": 0
            #     }
            # }
        }

    def format_stream_response_as_openai(self, chunk_response:str,is_last=False):
        finish_reason = "stop" if is_last else None
        return {
            # "id":"chatcmpl-123",
            "object":"chat.completion.chunk",
            "created":time.time(),
            "model": self.model_id,
            # "system_fingerprint": "fp_44709d6fcb",
            "choices":[
                {
                    "index":0,
                    "delta":{
                        "role":"assistant","content":chunk_response
                },
                "logprobs":None,
                "finish_reason":finish_reason}]
        }



    def invoke(self, request:dict):
        generate_kwargs = {
            "max_new_tokens":512,
            "temperature":0.01
        }
        tokenize_kwargs = {
            "chat_template":None
        }
        messages = request['messages']
        generate_kwargs = {
            **generate_kwargs,
            **request.get('generate_kwargs',{})
        }
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            **tokenize_kwargs
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        logger.info(f'request: {request}')
        logger.info(f"model_inputs: {model_inputs}, generate_kwargs: {generate_kwargs}")

        if not request.get('stream',False):
            generated_ids = self.model.generate(
                **model_inputs,
                **generate_kwargs
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]

            response = "".join(self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0])
            response = self.format_response_as_openai(response)
            logger.info(f'response: {response}')
            return response


        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True,skip_special_tokens=True)
        generation_kwargs = {
            **model_inputs,
            **generate_kwargs,
            "streamer":streamer
        }
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        def streamer_return_helper():
            history_response = ""
            for new_text in streamer:
                history_response += new_text
                new_text = self.format_stream_response_as_openai(new_text)
                if self.service_type == ServiceType.SAGEMAKER:
                    yield json.dumps(new_text) + "\n"
                else:
                    yield new_text

            new_text = self.format_stream_response_as_openai("",is_last=True)
            if self.service_type == ServiceType.SAGEMAKER:
                yield json.dumps(new_text) + "\n"
            else:
                yield new_text
            logger.info(f'response: {self.format_response_as_openai(history_response)}')

        return streamer_return_helper()
