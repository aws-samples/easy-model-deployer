from .invoker_base import InvokerBase
from emd.constants import MODEL_DEFAULT_TAG
import json
import os
import boto3

class ComfyUIInvoker(InvokerBase):
    def __init__(self, model_id, model_tag = MODEL_DEFAULT_TAG):
        super().__init__(model_id, model_tag)
        self.inputs = []

    def add_input(self, input:str):
        self.inputs = input


    def invoke(self):
        file_path = os.path.abspath(__file__)
        workflow_path = os.path.join(os.path.dirname(file_path), "../../pipeline/backend/comfyui/ltxvideo-txt2video-api.json")
        with open(workflow_path) as f:
            workflow = json.load(f)
            workflow["87"]["inputs"]["text"] = self.inputs
            pyload = {
                "workflow": workflow
            }
            ret = self._invoke(pyload)
            print(ret)
            s3_output_path = ret.get("output_path", None)
            s3_bucket = s3_output_path.split("/")[2]
            s3_video_path = "/".join(s3_output_path.split("/")[3:]) + "/LTXVideo_00001.mp4"
            prompt_id = ret.get("prompt_id", None)
            local_video_path = f"{prompt_id}.mp4"
            boto3.client("s3").download_file(s3_bucket, s3_video_path, local_video_path)
            ret["local_video_path"] = local_video_path
            return ret
