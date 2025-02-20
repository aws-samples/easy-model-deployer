from .invoker_base import InvokerBase
from emd.constants import MODEL_DEFAULT_TAG

class EmbeddingInvoker(InvokerBase):
    def __init__(self, model_id, model_tag = MODEL_DEFAULT_TAG):
        super().__init__(model_id, model_tag)
        self.inputs = []

    def add_input(self, input:str):
        self.inputs.append(input)

    def invoke(self):
        pyload = {
            "input": self.inputs
        }
        ret = self._invoke(pyload)
        return ret
