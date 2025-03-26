from .invoker_base import InvokerBase
from emd.constants import MODEL_DEFAULT_TAG

class RerankInvoker(InvokerBase):
    def __init__(self, model_id, model_tag = MODEL_DEFAULT_TAG):
        super().__init__(model_id, model_tag)
        self.text_a = None
        self.text_b = None

    def add_text_a(self, text:str):
        self.text_a = text

    def add_text_b(self, text:str):
        self.text_b = text

    def invoke(self):
        pyload = {
            "encoding_format": "float",
            "query": self.text_a,
            "documents": [self.text_b]
        }
        ret = self._invoke(pyload)
        return ret
