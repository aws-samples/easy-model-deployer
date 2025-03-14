import json
import os
from typing import Optional,Dict,Any,Union
import io
from urllib.parse import urlparse
from pydantic import model_validator
import uuid
import codecs
import time
from functools import reduce
import botocore
import threading
from botocore.exceptions import WaiterError
from botocore.exceptions import ClientError

from .client_base import ClientBase
from emd.utils.aws_service_utils import check_stack_exists,get_model_stack_info
from emd.models import Model
from emd.constants import MODEL_DEFAULT_TAG
from emd.utils.logger_utils import get_logger
from emd.utils.framework_utils import get_model_specific_path
import requests


logger = get_logger(__name__)


class LineIterator:
    """
    A helper class for parsing the byte stream input.

    The output of the model will be in the following format:

    b'{"outputs": [" a"]}\n'
    b'{"outputs": [" challenging"]}\n'
    b'{"outputs": [" problem"]}\n'
    ...


    This class accounts for this by concatenating bytes written via the 'write' function
    and then exposing a method which will return lines (ending with a '\n' character)
    within the buffer via the 'scan_lines' function.
    It maintains the position of the last read position to ensure
    that previous bytes are not exposed again.

    For more details see:
    https://aws.amazon.com/blogs/machine-learning/elevating-the-generative-ai-experience-introducing-streaming-support-in-amazon-sagemaker-hosting/
    """

    def __init__(self, stream: Any) -> None:
        self.byte_iterator = iter(stream)
        self.buffer = io.BytesIO()
        self.read_pos = 0

    def __iter__(self) -> "LineIterator":
        return self

    def __next__(self) -> Any:
        while True:
            self.buffer.seek(self.read_pos)
            line = self.buffer.readline()
            if line and line[-1] == ord("\n"):
                self.read_pos += len(line)
                return line[:-1]
            try:
                chunk = next(self.byte_iterator)
                # print('chunk: ',chunk)
            except StopIteration:
                if self.read_pos < self.buffer.getbuffer().nbytes:
                    # print('continue condition',self.read_pos,self.buffer.getbuffer().nbytes)
                    continue
                raise
            # if "PayloadPart" not in chunk:
            #     # Unknown Event Type
            #     continue
            self.buffer.seek(0, io.SEEK_END)
            self.buffer.write(chunk)#["PayloadPart"]["Bytes"])



class ECSClient(ClientBase):
    base_url:str = ""

    @model_validator(mode='before')
    def validate_environment(cls, values: Dict) -> Dict:
        if values.get("base_url"):
            return values

        model_stack_name = values.get("model_stack_name")
        if model_stack_name is None:
            # check if stack is ready
            model_id = values.get("model_id")
            if model_id is None:
                raise ValueError("model_id or model_stack_name must be provided")
            model_stack_name = Model.get_model_stack_name_prefix(
                model_id,
                model_tag=values.get("model_tag") or MODEL_DEFAULT_TAG
            )

        # get endpoint name from stack
        if not check_stack_exists(model_stack_name):
            raise ValueError(f"Model stack {model_stack_name} does not exist")

        stack_info = get_model_stack_info(model_stack_name)
        Outputs = stack_info.get('Outputs')
        if not Outputs:
            raise RuntimeError(f"Model stack {model_stack_name} does not have any outputs, the model may be not deployed in success")
        for output in Outputs:
            if output['OutputKey'] == 'PublicLoadBalancerDNSName':
                values["base_url"] = output['OutputValue']
                break

        assert values.get("base_url") is not None, "base_url  not found in stack outputs"
        return values

    def invoke(self,pyload:dict):
        stream = pyload.get('stream', False)
        model_specific_invocations_path = get_model_specific_path(self.model_id, self.model_tag, "invocations")
        url = f"{self.base_url}{model_specific_invocations_path}"
        if stream:
            response = requests.post(
                url,
                json=pyload,
                stream=True
            )
            if response.status_code != 200:
                raise RuntimeError(f"Error {response.status_code}, {response.text}")
            def _ret_iterator_helper():
                interator = LineIterator(response)
                for line in interator:
                    try:
                        decoded_line = line.decode('utf-8').strip()
                        if decoded_line.startswith('data: '):
                            json_data = decoded_line[len('data: '):]
                            chunk_dict = json.loads(json_data)
                            if not chunk_dict:
                                continue
                            yield chunk_dict
                    except Exception as e:
                        print(e)

            return _ret_iterator_helper()
        else:
            return requests.post(
                url,
                json=pyload
            ).json()
