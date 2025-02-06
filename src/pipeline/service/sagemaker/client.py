import boto3
import json
import sys
import io
import botocore
import re

from utils.LineIterator import LineIterator

class SageMakerClient:
    def __init__(self, region="us-east-1", endpoint_name="vllm-endpoint", stream=False):
        self.stream = stream
        self.client = boto3.client("runtime.sagemaker", region_name=region)
        self.endpoint_name = endpoint_name
        # self.model = model

    def invoke(self, request):
        # request["model"] = self.model
        if self.stream:
            request["stream"] = True
            response = self.client.invoke_endpoint_with_response_stream(
                EndpointName=self.endpoint_name,
                Body=json.dumps(request),
                ContentType="application/json",
            )
            event_stream = response['Body']
            for line in LineIterator(event_stream):
                print(line, end="")
                sys.stdout.flush()
        else:
            response = self.client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                Body=json.dumps(request),
                ContentType="application/json",
            )
            resp_body = response['Body']
            print('Response:')
            print(resp_body)
            assert isinstance(resp_body, botocore.response.StreamingBody)
            buffer = ''
            for line in resp_body.iter_chunks():
                data_str = line.decode('utf-8')
                print(data_str, end="")
                sys.stdout.flush()
            print('')