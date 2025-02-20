import os
import copy
import time
import json
import uuid

from typing import Optional
from pydantic import ValidationError
from backend.backend import BackendBase
from typing import Iterable, List
import requests
import boto3
import logging
from aiohttp import web
import websocket

from utils.common import sync_s3_files_or_folders_to_local, sync_local_outputs_to_s3


# ROOT_PATH = '/home/ubuntu/ComfyUI'
ROOT_PATH = "ComfyUI"
SERVER_ADDRESS = "127.0.0.1:8188"
URL_PING = f"http://{SERVER_ADDRESS}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ok(body: dict):
    return web.Response(
        status=200, content_type="application/json", body=json.dumps(body)
    )


class ComfyUIBackend(BackendBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_id = self.execute_model.model_id
        self.model_s3_bucket = self.execute_model.executable_config.model_s3_bucket
        self.api_base = f"{URL_PING}/prompt"
        self.s3_client = boto3.client("s3")
        self.client_id = str(uuid.uuid4())
        environ = {}  # Environment dictionary
        socket = None  # Socket object
        rfile = None  # File-like object for reading
        self.ws = websocket.WebSocket(environ, socket, rfile)
        with open("backend/comfyui/ltxvideo-txt2video-api.json") as f:
            self.workflow = json.load(f)

    def start(self):
        model_dir = f"emd_models/{self.model_id}"
        logger.info(f"Downloading model from s3")
        sync_s3_files_or_folders_to_local(self.model_s3_bucket, model_dir, ROOT_PATH)
        os.system("bash backend/comfyui/start.sh > comfyui.log 2>&1 &")
        while True:
            try:
                self.ws.connect(
                    "ws://{}/ws?clientId={}".format(SERVER_ADDRESS, self.client_id)
                )
                logger.info(f"Connected to comfyui websocket")
                break
            except Exception as e:
                logger.info(
                    f"The comfyui websocket is not ready yet, retrying in 10 second"
                )
                time.sleep(10)
                continue
        return

    def invoke(self, request):
        if "prompt" in request:
            prompt = request["prompt"]
            workflow = copy.deepcopy(self.workflow)
            # Replace the prompt in the workflow
            # workflow["120"]["inputs"]["text"] = prompt
            # Add the prompt to video generation
            workflow["87"]["inputs"]["text"] += prompt
            comfyui_req = {"prompt": workflow, "client_id": self.client_id}
        else:
            comfyui_req = {"prompt": request["workflow"], "client_id": self.client_id}
        data = json.dumps(comfyui_req).encode("utf-8")
        print(data)
        response = requests.post(self.api_base, data=data)
        response_data = response.json()
        print(response_data)
        prompt_id = response_data["prompt_id"]
        out_path = response_data.get("out_path", None)
        logger.info(f"prompt_id is {prompt_id}")
        # logger.info(f'out_path is {out_path}')
        s3_out_path = (
            f"output/{prompt_id}/{out_path}"
            if out_path is not None
            else f"output/{prompt_id}"
        )
        s3_temp_path = (
            f"temp/{prompt_id}/{out_path}"
            if out_path is not None
            else f"temp/{prompt_id}"
        )
        local_out_path = (
            f"{ROOT_PATH}/output/{out_path}"
            if out_path is not None
            else f"{ROOT_PATH}/output"
        )
        # local_temp_path = f'{ROOT_PATH}/temp/{out_path}' if out_path is not None else f'{ROOT_PATH}/temp'
        logger.info(
            f"s3_out_path is {s3_out_path} and local_out_path is {local_out_path}"
        )
        try:
            while True:
                out = self.ws.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    print("!!!!!!!!", message["type"])
                    if message["type"] == "executing":
                        data = message["data"]
                        print(data["prompt_id"])
                        if data["node"] is None and data["prompt_id"] == prompt_id:
                            logger.info(f"Execution is done for prompt_id {prompt_id}")
                            break  # Execution is done
                else:
                    continue  # previews are binary data
            # logger.info(f"Start to sync outputs to s3 for prompt_id {prompt_id}")
            sync_local_outputs_to_s3(self.model_s3_bucket, s3_out_path, local_out_path)
            # sync_local_outputs_to_s3(self.model_s3_bucket, s3_temp_path, local_temp_path)
            logger.info(f"Sync done to s3 for prompt_id {prompt_id}")
            response_body = {
                "prompt_id": prompt_id,
                "status": "success",
                "output_path": f"s3://{self.model_s3_bucket}/comfy/{s3_out_path}",
                # "temp_path": f's3://{self.model_s3_bucket}/comfy/{s3_temp_path}',
            }
            logger.info(f"execute inference response is {response_body}")
            return response_body
        except Exception as e:
            print(f"Error during processing: {str(e)}")
            raise

    def _transform_request(self, request):
        raise NotImplementedError

    def _transform_response(self, response):
        raise NotImplementedError

    def _get_response(self, response) -> List[str]:
        output = response
        return output
