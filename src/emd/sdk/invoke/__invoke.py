import json
import sys
import os
from typing import Iterable, List

import boto3
import botocore
import requests
from typing import Optional
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError
from typing_extensions import Annotated

from emd.utils.line_iterator import LineIterator


def get_streaming_response(response: requests.Response) -> Iterable[List[str]]:
    for chunk in response.iter_lines(chunk_size=64,
                                     decode_unicode=False,
                                     delimiter=b"\0"):
        if chunk:
            data_list = json.loads(chunk.decode("utf-8"))
            output = ""
            for data in data_list:
                output += data["choices"][0]["delta"]["content"]
            print(output, end="", flush=True)
            yield output

def clear_line(n: int = 1) -> None:
    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'
    for _ in range(n):
        print(LINE_UP, end=LINE_CLEAR, flush=True)

class SageMakerClient:
    def __init__(
        self,
        region="us-east-1",
        endpoint_name="vllm-endpoint",
        stream=False,
    ):
        self.stream = stream
        self.client = boto3.client("runtime.sagemaker", region_name=region)
        self.endpoint_name = endpoint_name

    def invoke(self, request):
        content = ""
        if self.stream:
            response = self.client.invoke_endpoint_with_response_stream(
                EndpointName=self.endpoint_name,
                Body=json.dumps(request),
                ContentType="application/json",
            )
            event_stream = response["Body"]
            for line in LineIterator(event_stream):
                print(line, end="")
                sys.stdout.flush()
                content += line
        else:
            response = self.client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                Body=json.dumps(request),
                ContentType="application/json",
            )
            resp_body = response["Body"]
            assert isinstance(resp_body, botocore.response.StreamingBody)
            # buffer = ""
            content = json.loads(resp_body.read().decode("utf-8"))
            # for line in resp_body.iter_chunks():
            #     data_str = line.decode("utf-8")
            #     print(data_str, end="")
            #     sys.stdout.flush()
            #     content += data_str
            print("")
        return content


class EC2Client:
    def __init__(self, host, model, stream=False):
        self.stream = stream
        self.host = host
        self.model = model

        from openai import OpenAI
        self.client = OpenAI(base_url=f"http://{self.host}/v1", api_key="xx")

    def invoke(self, request):
        content = ""
        request["model"] = self.model
        request["stream"] = self.stream
        response = requests.post(f"http://{self.host}/invocations", json=request)
        # num_printed_lines = 0
        for h in get_streaming_response(response):
            # clear_line(num_printed_lines)
            # num_printed_lines = 0
            print(h, end="", flush=True)
            # for i, line in enumerate(h):
                # num_printed_lines += 1
                # print(f"Beam candidate {i}: {line!r}", flush=True)
                # content += chunk.choices[0].delta.content
        return content
