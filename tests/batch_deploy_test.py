from emd import deploy as deploy_sdk, destroy as destroy_sdk
from pydantic import BaseModel
from emd.models import Model
from emd.models.utils.constants import ModelType
import traceback
from emd.utils.logger_utils import get_logger
import time

logger = get_logger(__name__)

class DeployConfig(BaseModel):
    model_id:str
    instance_type:str
    engine_type:str
    service_type:str
    framework_type:str
    model_tag:str
    extra_params: dict



class InvokeConfig(BaseModel):
    pyloads:list[dict]


class Task(BaseModel):
    deploy_config: DeployConfig
    invoke_config: InvokeConfig



def deploy(task:Task):
    model_id = task.deploy_config.model_id
    print("=="*50 + f"deploy: {model_id}" + "=="*50)
    deploy_sdk(
        model_id=task.deploy_config.model_id,
        instance_type=task.deploy_config.instance_type,
        engine_type=task.deploy_config.engine_type,
        service_type=task.deploy_config.service_type,
        framework_type=task.deploy_config.framework_type,
        model_tag=task.deploy_config.model_tag,
        extra_params=task.deploy_config.extra_params
    )

def invoke(task:Task):
    model_id = task.deploy_config.model_id
    print("=="*50 + f"invoke: {model_id}" + "=="*50)
    model_id = task.deploy_config.model_id
    model_tag = task.deploy_config.model_tag
    model = Model.get_model(model_id)

    model_type = model.model_type
    invoker_cls = None
    if model_type == ModelType.LLM:
        from emd.sdk.invoke.conversation_invoker import ConversationInvoker
        invoker_cls = ConversationInvoker
        # return conversation_invoke(model_id,model_tag)
    elif model_type == ModelType.WHISPER:
        from emd.sdk.invoke.whisper_invoker import WhisperInvoker
        invoker_cls = WhisperInvoker
    elif model_type == ModelType.EMBEDDING:
        from emd.sdk.invoke.embedding_invoker import EmbeddingInvoker
        invoker_cls = EmbeddingInvoker

    elif model_type == ModelType.VLM:
        from emd.sdk.invoke.vlm_invoker import VLMInvoker
        invoker_cls = VLMInvoker

    elif model_type == ModelType.RERANK:
        from emd.sdk.invoke.rerank_invoker import RerankInvoker
        invoker_cls = RerankInvoker

    elif model_type == ModelType.VIDEO:
        from emd.sdk.invoke.comfyui_invoke import ComfyUIInvoker
        invoker_cls = ComfyUIInvoker
    else:
        raise NotImplementedError

    invoker = invoker_cls(model_id=model_id, model_tag=model_tag)
    for pyload in task.invoke_config.pyloads:
        print(f"invoke with pyload: {pyload}")
        ret = invoker._invoke(pyload)
        print(f"invoke res: {ret}")

def destroy(task:Task):
    model_id = task.deploy_config.model_id
    print("=="*50 + f"destroy: {model_id}" + "=="*50)
    destroy_sdk(
        model_id=task.deploy_config.model_id,
        model_tag=task.deploy_config.model_tag
    )

def test_one_task(task:Task):
    print(f"task: \n{task.model_dump()}")
    model_id = task.deploy_config.model_id
    ret = {
        "code":0,
        "task":task,
        "error":"",
        "deploy_time":None,
        "invoke_time":None,
        "destroy_time":None
    }
    try:
        t0 = time.time()
        deploy(task)
        t1 = time.time()
        ret['deploy_time'] = t1-t0
        invoke(task)
        t2 = time.time()
        ret['invoke_time'] = t2-t1
        destroy(task)
        t3 = time.time()
        ret['destroy_time'] = t3-t2

        logger.info(f"task: {model_id} success")
    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"task: {model_id} failed:\n{error}")
        ret["code"] = 1
        ret["error"] = error
        try:
            destroy(task)
        except:
            error = traceback.format_exc()
            logger.error(f"task: {model_id} destroy failed:\n{error}")

    result = f"""\
<deploy_test_result>
<model_id>{model_id}</model_id>
<test_code>{ret['code']}</test_code>
<test_error>{ret['error']}</test_error>
<deploy_time>{ret['deploy_time']}</deploy_time>
<invoke_time>{ret['invoke_time']}</invoke_time>
<destroy_time>{ret['destroy_time']}</destroy_time>
</deploy_test_result>
"""
    logger.info(f"task: {model_id} test result:\n{result}")
    ret['summary'] = result
    return ret


if __name__ == "__main__":
    tasks = [
        {
            "deploy_config":{
                "model_id": "Qwen2.5-0.5B-Instruct",
                "instance_type":"g5.2xlarge",
                "engine_type":"vllm",
                "service_type":"sagemaker",
                "framework_type":"fastapi",
                "model_tag":"batch_test"
            },
            "invoke_config":{
                "pyloads":[{
                    "messages": [
                        {
                            "role": "user",
                            "content": "Explain async programming in Python"
                        }
                    ]
                }],
            }
        },
        {
            "deploy_config":{
                "model_id": "bge-base-en-v1.5",
                "instance_type":"g5.xlarge",
                "engine_type":"vllm",
                "service_type":"sagemaker",
                "framework_type":"fastapi",
                "model_tag":"batch_test"
            },
            "invoke_config":{
                "pyloads":[{
                    "input": ['Who you are?']
                }],
            }
        },
        {
            "deploy_config":{
                "model_id": "bge-reranker-v2-m3",
                "instance_type":"g5.xlarge",
                "engine_type":"vllm",
                "service_type":"sagemaker",
                "framework_type":"fastapi",
                "model_tag":"batch_test"
            },
            "invoke_config":{
                "pyloads":[{
                    "encoding_format": "float",
                    "text_1": "What's the capital of China?",
                    "text_2": "Beijing"
                }],
            }
        }
    ]
    tasks = [Task(**task) for task in tasks]
    test_ret = []
    for task in tasks:
        test_ret.append(test_one_task(task))

    # print test ret
    print("=="*50 + "test ret" + "=="*50)
    for ret in test_ret:
        task = ret['task']
        model_id = task.deploy_config.model_id
        result = f"""\
<deploy_test_result>
<model_id>{model_id}</model_id>
<test_code>{ret['code']}</test_code>
<test_error>{ret['error']}</test_error>
<deploy_time>{ret['deploy_time']}</deploy_time>
<invoke_time>{ret['invoke_time']}</invoke_time>
<destroy_time>{ret['destroy_time']}</destroy_time>
</deploy_test_result>
"""
        # print(f"<model_id: {model_id}\ntest code:{ret['code']}\nerror:{ret['error']}")
        print("=="*50)

    if all([ret['code'] == 0 for ret in test_ret]):
        print("=="*50 + "all success" + "=="*50)
