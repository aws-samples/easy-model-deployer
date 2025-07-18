from typing import Iterable, List
import os
import time
import base64
import io

from emd.models.utils.constants import ModelType,ServiceType

from backend.backend import BackendBase
from utils.common import download_dir_from_s3_by_s5cmd
import torch
from emd.constants import EMD_MODELS_LOCAL_DIR_TEMPLATE
from emd.utils.logger_utils import get_logger
from threading import Thread
import json
from transformers import AutoModel
from PIL import Image


logger = get_logger(__name__)

class TransformerEmbeddingBackend(BackendBase):
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
        self.is_bge_vl = "bge-vl" in self.model_id.lower()


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

        self.model = AutoModel.from_pretrained(
                model_abs_path,
                device_map="cuda",
                **self.pretrained_model_init_kwargs
        )

        # BGE-VL specific initialization
        if self.is_bge_vl:
            try:
                self.model.set_processor(model_abs_path)
                logger.info(f"BGE-VL processor set successfully for model: {self.model_id}")
            except Exception as e:
                logger.warning(f"Failed to set BGE-VL processor: {e}")

        logger.info(f"model: {self.model}")
        # TODO add tokenizer init args from model's definition
        # self.tokenizer =  AutoTokenizer.from_pretrained(
        #     model_abs_path,
        #     **self.pretrained_tokenizer_init_kwargs
        # )


    def format_openai_response(self,responses:list[list[float]]):
        return {
            "object": "list",
            "data": [
                {
                "object": "embedding",
                "index": i,
                "embedding": response
                }
                for i,response in enumerate(responses)
            ],
            "model": self.model_id,
            "usage": {
                "prompt_tokens": None,
                "total_tokens": None
            }
        }

    def _process_base64_image(self, image_data: str) -> Image.Image:
        """Convert base64 string to PIL Image"""
        try:
            # Handle data URL format
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]

            # Decode base64
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')

            return image
        except Exception as e:
            logger.error(f"Failed to process base64 image: {e}")
            raise ValueError(f"Invalid image data: {e}")

    def _convert_pil_to_bytesio(self, pil_image: Image.Image) -> io.BytesIO:
        """Convert PIL Image to BytesIO object for BGE-VL compatibility"""
        try:
            img_buffer = io.BytesIO()
            # Save as JPEG to ensure compatibility with BGE-VL model
            pil_image.save(img_buffer, format='JPEG', quality=95)
            img_buffer.seek(0)  # Reset pointer to beginning
            return img_buffer
        except Exception as e:
            logger.error(f"Failed to convert PIL image to BytesIO: {e}")
            raise ValueError(f"Image conversion failed: {e}")

    def _parse_multimodal_inputs(self, inputs):
        """Parse and categorize multimodal inputs for BGE-VL"""
        text_inputs = []
        image_inputs = []
        multimodal_inputs = []

        for inp in inputs:
            if isinstance(inp, str):
                # Simple text input
                text_inputs.append(inp)
            elif isinstance(inp, dict):
                if inp.get('type') == 'text':
                    text_inputs.append(inp.get('content', ''))
                elif inp.get('type') == 'image':
                    # Image-only input
                    image_data = inp.get('image') or inp.get('content')
                    if image_data:
                        pil_image = self._process_base64_image(image_data)
                        # Convert PIL Image to BytesIO for BGE-VL compatibility
                        bytesio_image = self._convert_pil_to_bytesio(pil_image)
                        image_inputs.append(bytesio_image)
                elif inp.get('type') == 'multimodal':
                    # Text + Image input
                    text = inp.get('text', '')
                    image_data = inp.get('image')
                    if image_data:
                        pil_image = self._process_base64_image(image_data)
                        # Convert PIL Image to BytesIO for BGE-VL compatibility
                        bytesio_image = self._convert_pil_to_bytesio(pil_image)
                        multimodal_inputs.append((text, bytesio_image))

        return text_inputs, image_inputs, multimodal_inputs

    def _generate_bge_vl_embeddings(self, inputs):
        """Generate embeddings using BGE-VL model"""
        text_inputs, image_inputs, multimodal_inputs = self._parse_multimodal_inputs(inputs)
        all_embeddings = []

        # Process text-only inputs
        if text_inputs:
            try:
                # Use explicit text= parameter for BGE-VL model
                text_embeddings = self.model.encode(text=text_inputs)
                if hasattr(text_embeddings, 'tolist'):
                    all_embeddings.extend(text_embeddings.tolist())
                else:
                    all_embeddings.extend(text_embeddings)
            except Exception as e:
                logger.error(f"Failed to encode text inputs: {e}")
                raise ValueError(f"BGE-VL text encoding failed: {e}")

        # Process image-only inputs
        if image_inputs:
            try:
                # Use explicit images= parameter with list format
                image_embeddings = self.model.encode(images=image_inputs)
                if hasattr(image_embeddings, 'tolist'):
                    all_embeddings.extend(image_embeddings.tolist())
                else:
                    all_embeddings.extend(image_embeddings)
            except Exception as e:
                logger.error(f"Failed to encode image inputs: {e}")
                raise ValueError(f"BGE-VL image encoding failed: {e}")

        # Process multimodal inputs (text + image)
        if multimodal_inputs:
            for text, bytesio_image in multimodal_inputs:
                try:
                    # Use explicit parameters with list format for both text and images
                    multimodal_embedding = self.model.encode(text=[text], images=[bytesio_image])
                    if hasattr(multimodal_embedding, 'tolist'):
                        all_embeddings.append(multimodal_embedding.tolist())
                    else:
                        all_embeddings.append(multimodal_embedding)
                except Exception as e:
                    logger.error(f"Failed to encode multimodal input: {e}")
                    raise ValueError(f"BGE-VL multimodal encoding failed: {e}")

        return all_embeddings

    def invoke(self, request:dict):
        inputs = request['input']
        if not inputs:
            return []

        logger.info(f'request: {request}')
        t0 = time.time()

        if self.is_bge_vl:
            # Use BGE-VL multimodal processing
            embeddings_list = self._generate_bge_vl_embeddings(inputs)
        else:
            # Use standard text embedding processing
            task = request.get('task', 'text-matching')
            truncate_dim = request.get('truncate_dim', None)
            embeddings = self.model.encode(inputs, task=task, truncate_dim=truncate_dim)
            embeddings_list = embeddings.tolist()

        logger.info(f'embeddings generated, count: {len(embeddings_list)}, elapsed time: {time.time()-t0}')
        return self.format_openai_response(embeddings_list)

    async def ainvoke(self, request: dict):
        """Async version of invoke method"""
        return self.invoke(request)
