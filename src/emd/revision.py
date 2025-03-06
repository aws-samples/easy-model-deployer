# import importlib.metadata
VERSION = "0.0.0"
COMMIT_HASH = "00000000"

def convert_version_name_to_stack_name(version_name:str):
    return version_name.replace(".","-")

def convert_stack_name_to_version_name(stack_name:str):
    return stack_name.replace("-",".")
