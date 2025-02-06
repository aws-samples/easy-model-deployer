import json
import os

import questionary

def deploy_vllm_on_sagemaker(model_id, backend):
    print(f"Deploying {model_id} on sagemaker with backend {backend}")
    os.system(f"bash src/deploy/on_sagemaker/deploy.sh {model_id} {backend}")

def deploy_vllm_on_ec2(model_id, backend):
    print(f"Deploying {model_id} on ec2 with backend {backend}")
    os.system(f"bash src/deploy/on_ec2/deploy.sh {model_id} {backend}")

def deploy_comfui_on_sagemaker(model_id):
    print(f"Deploying {model_id} on sagemaker with backend comfui")

def deploy_comfui_on_ec2(model_id):
    print(f"Deploying {model_id} on ec2 with backend comfui")

def deploy(model_id, platform, backend):
    if platform == "SageMaker" and backend == "vllm":
        deploy_vllm_on_sagemaker(model_id, backend)
    elif platform == "EC2" and backend == "vllm":
        deploy_vllm_on_ec2(model_id, backend)
    elif platform == "SageMaker" and backend == "comfui":
        deploy_comfui_on_sagemaker(model_id)
    elif platform == "ec2" and backend == "comfui":
        deploy_comfui_on_ec2(model_id)

if __name__ == "__main__":
    app_info = json.load(open("model_info.json"))
    selected_app = questionary.select(
        "What app do you want to deploy?",
        choices=app_info.keys()
    ).ask()

    model_choices = app_info[selected_app].keys()
    selected_model_id = questionary.select(
        "What model you want to deploy?",
        choices=model_choices
    ).ask()

    platform_choices = app_info[selected_app][selected_model_id]["platforms"]
    selected_platform = questionary.select(
        "What platform do you want to deploy on?",
        choices=platform_choices
    ).ask()

    backend_choices = app_info[selected_app][selected_model_id]["backends"]
    selected_backend = questionary.select(
        "What backend do you want to use?",
        choices=backend_choices
    ).ask()

    instance_type_choices = app_info[selected_app][selected_model_id]["instance_types"]
    if selected_platform != 'EC2':
        selected_instance_type = questionary.select(
            "What instance type do you want to use?",
            choices=instance_type_choices
        ).ask()

    start_deploy_choices = ["Yes", "No"]
    selected_start_deploy_choices = questionary.rawselect(
        "Do you want to start the deployment?",
        choices=start_deploy_choices
    ).ask()

    if selected_start_deploy_choices == "Yes":
        print(f"Starting deployment of {selected_model_id} on {selected_platform} with backend {selected_backend}")
        deploy(selected_model_id, selected_platform, selected_backend)