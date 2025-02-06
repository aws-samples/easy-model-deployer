from dmaa import deploy as deploy_sdk, destroy as destroy_sdk
from pydantic import BaseModel 
from dmaa.models import Model 
from dmaa.models.utils.constants import ModelType
import traceback 
from dmaa.utils.logger_utils import get_logger


logger = get_logger(__name__)

class DeployConfig(BaseModel):
    model_id:str
    instance_type:str
    engine_type:str
    service_type:str
    framework_type:str
    model_tag:str


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
        model_tag=task.deploy_config.model_tag
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
        from dmaa.sdk.invoke.conversation_invoker import ConversationInvoker
        invoker_cls = ConversationInvoker
        # return conversation_invoke(model_id,model_tag)
    elif model_type == ModelType.WHISPER:
        from dmaa.sdk.invoke.whisper_invoker import WhisperInvoker
        invoker_cls = WhisperInvoker
    elif model_type == ModelType.EMBEDDING:
        from dmaa.sdk.invoke.embedding_invoker import EmbeddingInvoker
        invoker_cls = EmbeddingInvoker
        
    elif model_type == ModelType.VLM:
        from dmaa.sdk.invoke.vlm_invoker import VLMInvoker
        invoker_cls = VLMInvoker
        
    elif model_type == ModelType.RERANK:
        from dmaa.sdk.invoke.rerank_invoker import RerankInvoker
        invoker_cls = RerankInvoker
        
    elif model_type == ModelType.VIDEO:
        from dmaa.sdk.invoke.comfyui_invoke import ComfyUIInvoker
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
    model_id = task.deploy_config.model_id
    ret = {
        "code":0,
        "task":task,
        "error":0
    }
    try:
        deploy(task)
        invoke(task)
        destroy(task)
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
        print(f"model_id: {model_id}\ntest code:{ret['code']}\nerror:{ret['error']}")
        print("=="*50)

    if all([ret['code'] == 0 for ret in test_ret]):
        print("=="*50 + "all success" + "=="*50)



