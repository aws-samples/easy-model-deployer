# conversation invoke
from .invoker_base import InvokerBase
from emd.constants import MODEL_DEFAULT_TAG
import base64
import os
import io
from urllib.parse import urlparse
from rich.console import Console

class VLMInvoker(InvokerBase):
    def __init__(self, model_id, model_tag = MODEL_DEFAULT_TAG):
        super().__init__(model_id, model_tag)
        self.image_path = None
        self.use_message = None
        self.sample_audio_path = self.assets_path + "/vlm_sample_data.jpg"
        console = Console()
        console.print(f"VLM sample data path: {self.sample_audio_path}")

    def add_user_message(self, message):
        self.use_message = message

    def add_image(self, image_path):
        self.image_path = image_path

    def convert_image_path_to_base64(self,image_path:str):
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        elif image_path.startswith("s3://"):
            # download image from s3
            import boto3
            s3 = boto3.client('s3')
            o = urlparse(image_path, allow_fragments=False)
            buffer = io.BytesIO()
            bucket,object_name = o.netloc,o.path.lstrip("/")
            s3.download_fileobj(bucket, object_name, buffer)
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode('utf-8')
        else:
            raise Exception(f"image_path: {image_path} is not valid, only local file and s3 files  are allowed")


    def invoke(self,stream=False):
        image_path = self.image_path
        use_message = self.use_message
        image_type = image_path.split(".")[-1]
        image_base64 = self.convert_image_path_to_base64(image_path)
        pyload = {
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": use_message},
                    {"type": "image_url", "image_url": {"url": f"data:image/{image_type};base64,{image_base64}"}},
                ]
            }],
            "stream": stream
        }
        ret = self._invoke(pyload)
        if not stream:
            return ret['choices'][0]['message']['content']

        def _stream_helper():
            for i in ret:
                yield i

        return _stream_helper()
