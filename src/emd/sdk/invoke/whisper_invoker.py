from .invoker_base import InvokerBase
from emd.constants import MODEL_DEFAULT_TAG
from rich.console import Console


class WhisperInvoker(InvokerBase):
    def __init__(self, model_id, model_tag = MODEL_DEFAULT_TAG):
        super().__init__(model_id, model_tag)
        self.audio_input_path = None
        self.model = None
        self.bucket = None
        self.key = None
        self.config = {}
        self.sample_audio_path = self.assets_path + "/asr_sample_data.wav"
        console = Console()
        console.print(f"ASR sample data path: {self.sample_audio_path}")

    def add_audio_input(self,path):
        self.audio_input_path = path

    def add_model(self, model):
        self.model = model

    def add_bucket(self, bucket):
        self.bucket = bucket

    def add_key(self, key):
        self.key = key

    def add_config(self, config):
        self.config = config

    def invoke(self):
        pyload = {
            "audio_input": self.audio_input_path,
            "model": self.model,
            "bucket":self.bucket,
            "key": self.key,
            "config": self.config
        }
        ret = self._invoke(pyload)
        return ret
