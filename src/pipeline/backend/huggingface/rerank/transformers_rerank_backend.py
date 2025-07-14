from typing import Iterable, List
import os
import time

from emd.models.utils.constants import ModelType,ServiceType

from backend.backend import BackendBase
from utils.common import download_dir_from_s3_by_s5cmd
import torch
from emd.constants import EMD_MODELS_LOCAL_DIR_TEMPLATE
from emd.utils.logger_utils import get_logger
from threading import Thread
import json
from transformers import AutoModelForSequenceClassification


logger = get_logger(__name__)

class TransformerRerankBackend(BackendBase):
    def __init__(self,*args,**kwargs):
        super().__init__(
              *args,
              **kwargs
        )

        self.model_id = self.execute_model.model_id
        self.model_s3_bucket = self.execute_model.executable_config.model_s3_bucket
        self.model_files_s3_path = self.execute_model.model_files_s3_path
        self.service_type = self.execute_model.executable_config.current_service.service_type
        # self.gpu_num = torch.cuda.device_count()
        self.model_type = self.execute_model.model_type
        self.proc = None
        self.model = None
        self.pretrained_model_init_kwargs = self.execute_model.executable_config.current_engine.pretrained_model_init_kwargs or {}


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
        torch_dtype = self.pretrained_model_init_kwargs.get("torch_dtype")
        if torch_dtype is not None:
            self.pretrained_model_init_kwargs['torch_dtype'] = {
             "float16":torch.float16,
             "float32":torch.float32,
             "float64":torch.float64,
             "bfloat16":torch.bfloat16
            }[torch_dtype]

        self.model = AutoModelForSequenceClassification.from_pretrained(
                model_abs_path,
                device_map="cuda",
                **self.pretrained_model_init_kwargs
        )
        logger.info(f"model: {self.model}")
        # TODO add tokenizer init args from model's definition
        # self.tokenizer =  AutoTokenizer.from_pretrained(
        #     model_abs_path,
        #     **self.pretrained_tokenizer_init_kwargs
        # )


    def format_vllm_response(self,documents:list[str],scores:list[float]):
        return {
            "id": None,
            "model": self.model_id,
            "usage": {
                "total_tokens": None
            },
            "results": [
                {
                "index": index,
                "document": {
                    "text": doc
                },
                "relevance_score": score
                }
                for index,(doc,score) in enumerate(zip(documents,scores))
            ]
        }

    def invoke(self, request:dict):
        query:list = request['query']
        documents:list[str] = request['documents']
        assert isinstance(query, str) and isinstance(documents, list) \
            and query and documents,(query,documents)

        sentence_pairs = [[query, doc] for doc in documents]
        t0 = time.time()
        scores = self.model.compute_score(sentence_pairs)
        if not isinstance(scores,list):
            scores = [scores]
        logger.info(f'rerank res: {scores},\nelapsed time: {time.time()-t0}')
        return self.format_vllm_response(documents, scores)
