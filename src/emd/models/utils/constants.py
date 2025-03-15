from enum import Enum, EnumMeta
from typing import ClassVar


class EnumDirectValueMeta(EnumMeta):
    def __getattribute__(cls, name):
        value = super().__getattribute__(name)
        if isinstance(value, cls):
            value = value.value
        return value

    def __call__(*args, **kwargs):
        r = EnumMeta.__call__(*args, **kwargs)
        return r.value


class ConstantBase(Enum, metaclass=EnumDirectValueMeta):
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def all_values(cls):
        return list(cls._value2member_map_.keys())


class EngineType(ConstantBase):
    VLLM = "vllm"
    HUGGINGFACE = "huggingface"
    COMFYUI = "comfyui"
    OLLAMA = "ollama"
    LLAMA_CPP = "llama.cpp"
    TGI = "tgi"
    LMDEPLOY = 'lmdeploy'

    # @classmethod
    # def get_engine_description(cls,engine_type:str):
    #     descriptions_map = {
    #         cls.VLLM: "VLLM is a high-performance inference engine that is designed to be easy to use and deploy.",
    #         cls.HUGGINGFACE: "Huggingface is a library that provides access to pre-trained models from Huggingface.",
    #         cls.CONFYUI: "ConfyUI is a library that provides access to pre-trained models from ConfyUI.",
    #         cls.OLLAMA: "Ollama is a lightweight, high-performance machine learning model server."
    #     }
    #     return descriptions_map[engine_type]


class InstanceType(ConstantBase):
    G4DNXLARGE = "g4dn.xlarge"
    G4DN2XLARGE = "g4dn.2xlarge"
    G4DN4XLARGE = "g4dn.4xlarge"
    G4DN8XLARGE = "g4dn.8xlarge"
    G4DN16XLARGE = "g4dn.16xlarge"
    G4DN12XLARGE = "g4dn.12xlarge"

    G5d48XLARGE = "g5.48xlarge"
    G5d24XLARGE = "g5.24xlarge"
    G5d12XLARGE = "g5.12xlarge"
    G5d16XLARGE = "g5.16xlarge"
    G5d2XLARGE = "g5.2xlarge"
    G5dXLARGE = "g5.xlarge"
    G5d4XLARGE = "g5.4xlarge"
    G5d8XLARGE = "g5.8xlarge"

    G6eXLARGE = "g6e.xlarge"
    G6e2XLARGE = "g6e.2xlarge"
    G6e4XLARGE = "g6e.4xlarge"
    G6e8XLARGE = "g6e.8xlarge"
    G6e16XLARGE = "g6e.16xlarge"
    G6e12XLARGE = "g6e.12xlarge"
    G6e24XLARGE = "g6e.24xlarge"
    G6e48XLARGE = "g6e.48xlarge"


    INF2D8XLARGE = "inf2.8xlarge"
    INF2DXLARGE = "inf2.xlarge"
    INF2D24XLARGE = "inf2.24xlarge"
    INF2D48XLARGE = "inf2.48xlarge"
    LOCAL = "local"

    @classmethod
    def convert_instance_type_to_sagemaker(cls, instance_type: str):
        assert cls.has_value(instance_type), instance_type
        if instance_type.startswith("ml."):
            return instance_type
        return f"ml.{instance_type}"

    @classmethod
    def convert_instance_type_to_ec2(cls, instance_type: str):
        assert cls.has_value(instance_type), instance_type
        return f"{instance_type}"

    @classmethod
    def convert_instance_type_to_ecs(cls, instance_type: str):
        assert cls.has_value(instance_type), instance_type
        return f"{instance_type}"

    @classmethod
    def convert_instance_type(cls, instance_type: str, service: str):
        if (
            service == ServiceType.SAGEMAKER
            or service == ServiceType.SAGEMAKER_ASYNC
        ):
            return cls.convert_instance_type_to_sagemaker(instance_type)
        elif service == ServiceType.EC2:
            return cls.convert_instance_type_to_ec2(instance_type)
        elif service == ServiceType.ECS:
            return cls.convert_instance_type_to_ecs(instance_type)
        elif service == ServiceType.LOCAL:
            return instance_type
        else:
            raise NotImplementedError(service)

class ServiceType(ConstantBase):
    SAGEMAKER = "sagemaker"
    SAGEMAKER_ASYNC = "sagemaker_async"
    EC2 = "ec2"
    ECS = "ecs"
    LOCAL = "local"

class FrameworkType(ConstantBase):
    FASTAPI = "fastapi"
    CUSTOM = "custom"

class ModelType(ConstantBase):
    LLM = "llm"
    WHISPER = "whisper"
    RERANK = "rerank"
    VLM = "vlm"
    EMBEDDING = "embedding"
    VIDEO = "video"

class ServiceCode(ConstantBase):
    SAGEMAKER = "sagemaker"

class ModelFilesDownloadSource(ConstantBase):
    HUGGINGFACE = "huggingface"
    MODELSCOPE= "modelscope"
    AUTO = "auto"

class ServiceQuotaCode(ConstantBase):

    G5dXLARGE_ENDPOINT = "L-1928E07B"
    G5d2XLARGE_ENDPOINT = "L-9614C779"
    G5d4XLARGE_ENDPOINT = "L-C1B9A48D"
    G5d8XLARGE_ENDPOINT = "L-065D610E"
    G5d12XLARGE_ENDPOINT = "L-65C4BD00"
    G5d16XLARGE_ENDPOINT = "L-962705EA"
    G5d24XLARGE_ENDPOINT = "L-6821867B"
    G5d48XLARGE_ENDPOINT = "L-0100B823"
    G6e2XLARGE_ENDPOINT = "L-F8D7F460"
    INF2DXLARGE_ENDPOINT = "L-C8AB7CDA"
    INF2D8XLARGE_ENDPOINT = "L-F761337C"
    INF2D24XLARGE_ENDPOINT = "L-9C39178F"
    INF2D48XLARGE_ENDPOINT = "L-286C98BC"
    @classmethod
    def get_service_quota_code(cls, instance_type: str):
        mapping = {
            InstanceType.G4DNXLARGE:"L-B67CFA0C",
            InstanceType.G4DN2XLARGE:"L-EA346344",
            InstanceType.G4DN4XLARGE:"L-31522FA6",
            InstanceType.G4DN8XLARGE:"L-7D28AD75",
            InstanceType.G4DN16XLARGE:"L-8679F6F3",
            InstanceType.G4DN12XLARGE:"L-07BEB181",

            InstanceType.G5dXLARGE: cls.G5dXLARGE_ENDPOINT,
            InstanceType.G5d2XLARGE: cls.G5d2XLARGE_ENDPOINT,
            InstanceType.G5d4XLARGE: cls.G5d4XLARGE_ENDPOINT,
            InstanceType.G5d8XLARGE: cls.G5d8XLARGE_ENDPOINT,
            InstanceType.G5d12XLARGE: cls.G5d12XLARGE_ENDPOINT,
            InstanceType.G5d16XLARGE: cls.G5d16XLARGE_ENDPOINT,
            InstanceType.G5d24XLARGE: cls.G5d24XLARGE_ENDPOINT,
            InstanceType.G5d48XLARGE: cls.G5d48XLARGE_ENDPOINT,
            InstanceType.G6eXLARGE: "G6e2XLARGE",
            InstanceType.G6e2XLARGE: cls.G6e2XLARGE_ENDPOINT,
            InstanceType.G6e4XLARGE: "L-93531071",
            InstanceType.G6e8XLARGE: "L-96A28D02",
            InstanceType.G6e16XLARGE: "L-2930A179",
            InstanceType.G6e12XLARGE: "L-60313EA3",
            InstanceType.G6e24XLARGE: "L-AE407E8B",
            InstanceType.G6e48XLARGE: "L-E0C458EA",

            InstanceType.INF2DXLARGE: cls.INF2DXLARGE_ENDPOINT,
            InstanceType.INF2D8XLARGE: cls.INF2D8XLARGE_ENDPOINT,
            InstanceType.INF2D24XLARGE: cls.INF2D24XLARGE_ENDPOINT,
            InstanceType.INF2D48XLARGE: cls.INF2D48XLARGE_ENDPOINT,
        }
        if instance_type not in mapping:
            raise ValueError(
                f"No service quota code found for instance type: {instance_type}"
            )
        return mapping[instance_type]


class ModelSeriesType(ConstantBase):
    GEMMA3 = "gemma3"
    QWEN2D5 = "qwen2.5"
    GLM4 = "glm4"
    INTERLM2d5 = "internlm2.5"
    WHISPER = "whisper"
    BGE = "bge"
    COMFYUI = "comfyui"
    QWEN2VL = "qwen2vl"
    INTERNVL25 = "internvl2.5"
    LLAMA = "llama"
    QWEN_REASONING_MODEL = "qwen reasoning model"
    DEEPSEEK_REASONING_MODEL = "deepseek reasoning model"
    DEEPSEEK_v3 = "deepseek v3"
    BAICHUAN = "baichuan"
