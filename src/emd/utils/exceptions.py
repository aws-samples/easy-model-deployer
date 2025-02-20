from emd.constants import ENV_STACK_NAME
class EnvStackNotExistError(Exception):
    def __init__(self,env_stack_name=ENV_STACK_NAME):
        super().__init__( f"Environment stack '{env_stack_name}' does not exist. Please run `emd bootstrap` to build the emd environment.")


class AWSCredentialsError(Exception):
    def __init__(self):
        super().__init__( "AWS credentials not found or invalid.\nPlease configure your AWS credentials using:\n`aws configure`")



class DmaaEnvStackNotReadyError(Exception):
    def __init__(self, env_stack_name=ENV_STACK_NAME):
        super().__init__( f"Environment stack '{env_stack_name}' is not ready. Please run `emd bootstrap` to build the emd environment.")



class ModelNotSupported(Exception):
    def __init__(self,region,model_id=None):
        if model_id is not None:
            super().__init__(f"model: {model_id} is not supported in region: {region}")
        else:
            super().__init__(f"No models are supported in region: {region}")

class ServiceNotSupported(Exception):
    def __init__(self,region,service_type=None):
        if service_type is not None:
            super().__init__(f"service: {service_type} is not supported in region: {region}")
        else:
            super().__init__(f"No valid services are supported in region: {region}")

class InstanceNotSupported(Exception):
    def __init__(self,region,instance_type=None):
        if instance_type is not None:
            super().__init__(f"instance: {instance_type} is not supported in region: {region}")
        else:
            super().__init__(f"No valid instances are supported in region: {region}")
