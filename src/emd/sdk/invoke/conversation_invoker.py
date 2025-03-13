# conversation invoke
from .invoker_base import InvokerBase
from emd.constants import MODEL_DEFAULT_TAG


class ConversationInvoker(InvokerBase):
    def __init__(self, model_id, model_tag = MODEL_DEFAULT_TAG):
        super().__init__(model_id, model_tag)
        self.messages = []

    def add_system_message(self,message:str):
        self.messages.insert({"role": "system", "content": message},0)

    def add_user_message(self,message:str):
        self.messages.append({"role": "user", "content": message})

    def add_assistant_message(self, message:str):
        self.messages.append({"role": "assistant", "content": message})

    def invoke(self,pyload=None,stream=False):
        if pyload is None:
            pyload = {
                "messages": self.messages,
                "stream": stream
            }
        ret = self._invoke(pyload)
        if not stream:
            try:
                ai_message = ret['choices'][0]['message']
                content = ai_message['content']
                reasoning_content = ai_message.get('reasoning_content','')
                if reasoning_content:
                        content = f"<Reasoning>\n{reasoning_content}\n</Reasoning>\n{content}"
                return content
            except Exception as e:
                return ret


        def _stream_helper():
            for i in ret:
                yield i

        return _stream_helper()
