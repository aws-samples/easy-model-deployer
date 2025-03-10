from emd.utils.aws_service_utils import get_model_stack_info, get_current_region
from emd.models import Model
from emd.constants import MODEL_DEFAULT_TAG
from emd.models.utils.constants import ServiceType
import emd
import os


class InvokerBase:
    def __init__(self,model_id:str,model_tag:str=MODEL_DEFAULT_TAG):
        self.model_id = model_id
        self.model_tag = model_tag
        self.model:Model = Model.get_model(model_id)
        self.model_stack_name = None
        self.service_type = None
        self.instance_type = None
        self.framework_type = None
        self.engine_type = None
        self.initialize()
        self.service_client = self.get_service_client(service_type=self.service_type)
        self.assets_path = os.path.dirname(emd.__file__) + "/sample"

    def initialize(self):
        model_stack_name = self.model.get_model_stack_name_prefix(
            self.model_id,
            self.model_tag
        )
        self.model_stack_name = model_stack_name
        stack_info = get_model_stack_info(self.model_stack_name)
        parameters = stack_info.get('Parameters')

        if not parameters:
            raise RuntimeError(f"Model stack {model_stack_name} does not have any outputs, the model may be not deployed in success")

        parameter_d = {}
        for parameter in parameters:
            parameter_d[parameter['ParameterKey']] = parameter['ParameterValue']

        self.service_type = parameter_d['ServiceType']
        self.instance_type = parameter_d['InstanceType']
        self.framework_type = parameter_d['FrameWorkType']
        self.engine_type = parameter_d['EngineType']


    def get_service_client(self,service_type:str):
        if service_type in [ServiceType.SAGEMAKER,ServiceType.SAGEMAKER_ASYNC]:
            from emd.sdk.clients.sagemaker_client import SageMakerClient
            return SageMakerClient(model_stack_name=self.model_stack_name, region_name=get_current_region())
        elif service_type == ServiceType.ECS:
            from emd.sdk.clients.ecs_client import ECSClient
            return ECSClient(model_stack_name=self.model_stack_name, region_name=get_current_region())
        else:
            raise ValueError(f"Service type {service_type} is not supported")


    def _invoke(self,pyload:dict):
        return InvokerBase.invoke(self,pyload)

    def invoke(self,pyload:dict):
        if self.service_type == ServiceType.SAGEMAKER_ASYNC:
            return self.service_client.invoke_async(pyload)
        return self.service_client.invoke(
            pyload
        )
