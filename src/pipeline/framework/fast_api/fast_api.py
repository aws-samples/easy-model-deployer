import os
import sys
import uvicorn
import argparse
import logging
from emd.models import Model,ExecutableConfig
from emd.models.utils.constants import FrameworkType
from emd.models.utils.serialize_utils import load_extra_params,dump_extra_params
from fastapi import FastAPI, Request, status, Header, Depends
from fastapi.responses import JSONResponse, Response, StreamingResponse
from emd.utils.logger_utils import get_logger
from fastapi.concurrency import run_in_threadpool
from emd.utils.framework_utils import get_model_specific_path

model_id = os.environ.get("model_id")
model_tag = os.environ.get("model_tag")
logger = get_logger(__name__)
logger.setLevel(logging.INFO)
logger.info(f"model_id: {model_id}")
logger.info(f"model_tag: {model_tag}")
# prevent logging ping
class HealthCheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("GET /ping") == -1 and record.getMessage().find("GET /health") == -1

# Remove /credentials/health from application server logs
logging.getLogger("uvicorn.access").addFilter(HealthCheckFilter())

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int,default=8080)
    # parser.add_argument("--uvicorn_log_level", type=str,default="info")
    parser.add_argument("--model_id", type=str)
    parser.add_argument("--backend_type", type=str)
    parser.add_argument("--model_s3_bucket", type=str, default="emd-models")
    parser.add_argument("--region", type=str)
    parser.add_argument("--instance_type", type=str)
    parser.add_argument("--service_type", type=str)
    # parser.add_argument("--engine_params", type=load_extra_params,default=os.environ.get("engine_params","{}"))
    parser.add_argument(
        "--extra_params",
        type=load_extra_params,
        default=os.environ.get("extra_params", "{}")
    )
    parser.add_argument("--framework_type", type=str,default=FrameworkType.FASTAPI)
    return parser.parse_args()

app = FastAPI()
engine = None

async def get_authorization(authorization: str = Header(None)):
    return authorization

async def invoke(payload):
    # generator = await run_in_threadpool(engine.invoke, payload)
    generator = await engine.ainvoke(payload)
    stream = payload.get("stream",False)
    if stream:
        return StreamingResponse(content=generator,
                                media_type="text/event-stream")
    else:
        return generator

# As sagemaker endpoint requires...
@app.get("/ping")
def ping():
    return JSONResponse(content={}, status_code=status.HTTP_200_OK)

@app.get("/health")
def health():
    return "200 OK"

# As sagemaker endpoint requires...
@app.post("/invocations")
@app.post("/v1/chat/completions")
@app.post("/v1/embeddings")
@app.post("/score")
# @measure_time
async def invocations(request: Request, authorization: str = Depends(get_authorization)):
    # logger.info('invocations ......')
    payload = await request.json()
    # If the request does not have Authorization, invoke the payload
    if authorization is None:
        return await invoke(payload)
    # If the request has extra_headers, add Authorization to it
    if "extra_headers" in payload and "Authorization" not in payload["extra_headers"]:
        payload["extra_headers"]["Authorization"] = authorization
    # If the request does not have extra_headers, create a new one with Authorization
    elif "extra_headers" not in payload:
        payload["extra_headers"] = { "Authorization": authorization }

    return await invoke(payload)

endpoints = {
    "ping": {"func": ping, "methods": ["GET"]},
    "health": {"func": health, "methods": ["GET"]},
    # Note: The functions for the POST endpoints all use "invocations".
    "invocations": {"func": invocations, "methods": ["POST"]},
    "v1/chat/completions": {"func": invocations, "methods": ["POST"]},
    "v1/embeddings": {"func": invocations, "methods": ["POST"]},
    "score": {"func": invocations, "methods": ["POST"]},
}

if model_id and model_tag:
    for base_path, route_info in endpoints.items():
        path = get_model_specific_path(model_id, model_tag, base_path)
        app.add_api_route(
            path=path,
            endpoint=route_info["func"],
            methods=route_info["methods"]
        )

if __name__ == "__main__":
    args = parse_args()
    host = args.host
    port = args.port
    # uvicorn_log_level = args.uvicorn_log_level
    model_id = args.model_id
    # continue generate the variables
    backend_type = args.backend_type
    model_s3_bucket = args.model_s3_bucket
    extra_params = args.extra_params
    # gpu_num = args.gpu_num
    instance_type = args.instance_type
    service_type = args.service_type
    # engine_params = extra_params.get("engine_params", {})
    # model_params = extra_params.get("model_params", {})
    framework_type = args.framework_type
    logger.info(f"extra_params: {extra_params}")

    model = Model.get_model(model_id)
    # get region
    execute_model = model.convert_to_execute_model(
        engine_type=backend_type,
        region=args.region,
        instance_type=instance_type,
        service_type=service_type,
        framework_type=framework_type,
        model_s3_bucket=model_s3_bucket,
        extra_params=extra_params,
        # model_tag=model_tag
    )
    logger.info(f"executable_config:\n{execute_model.executable_config.model_dump()}")
    engine = execute_model.get_engine()
    framework = execute_model.executable_config.current_framework
    engine.start()
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=framework.uvicorn_log_level,
        timeout_keep_alive=framework.timeout_keep_alive,
        limit_concurrency=framework.limit_concurrency,
    )
