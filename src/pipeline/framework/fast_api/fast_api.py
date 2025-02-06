import os
import sys
import uvicorn
import argparse
import logging
from dmaa.models import Model,ExecutableConfig
from dmaa.models.utils.constants import FrameworkType
from dmaa.models.utils.serialize_utils import load_extra_params,dump_extra_params
from fastapi import FastAPI, Request, status, Header, Depends
from fastapi.responses import JSONResponse, Response, StreamingResponse
from dmaa.utils.logger_utils import get_logger

logger = get_logger(__name__)
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
    parser.add_argument("--uvicorn_log_level", type=str,default="info")
    parser.add_argument("--model_id", type=str)
    parser.add_argument("--backend_type", type=str)
    parser.add_argument("--model_s3_bucket", type=str, default="dmaa-models")
    # parser.add_argument("--gpu_num", type=int, default=1)
    parser.add_argument("--instance_type", type=str)
    parser.add_argument("--service_type", type=str)
    parser.add_argument("--engine_params", type=load_extra_params,default=os.environ.get("engine_params","{}"))
    parser.add_argument("--framework_type", type=str,default=FrameworkType.FASTAPI)
    return parser.parse_args()

app = FastAPI()
engine = None

async def get_authorization(authorization: str = Header(None)):
    return authorization

async def invoke(payload):
    generator = engine.invoke(payload)
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

if __name__ == "__main__":
    args = parse_args()
    host = args.host
    port = args.port 
    uvicorn_log_level = args.uvicorn_log_level
    model_id = args.model_id
    # continue generate the variables
    backend_type = args.backend_type
    model_s3_bucket = args.model_s3_bucket
    # gpu_num = args.gpu_num
    instance_type = args.instance_type
    service_type = args.service_type
    engine_params = args.engine_params
    framework_type = args.framework_type
    logger.info(f"engine_params: {engine_params}")

    model = Model.get_model(model_id)
    engine = model.find_current_engine(backend_type)
    for k,v in engine_params.items():
        engine[k] = v
    executable_config = ExecutableConfig(
        current_engine=engine,
        current_instance=model.find_current_instance(instance_type),
        current_service=model.find_current_service(service_type),
        model_s3_bucket=model_s3_bucket,
        current_framework=model.find_current_framework(framework_type),
    )
    execute_model = model.convert_to_execute_model(
        executable_config
    )
    engine = execute_model.get_engine()
    engine.start()
    uvicorn.run(app, host=host, port=port, log_level=uvicorn_log_level, timeout_keep_alive=60)

