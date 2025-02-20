import os
import json

def qwen2d5_128k_model_files_hook(model_path,**kwargs):
    """To enable 128k inference, add rope_scaling kwargs from `https://huggingface.co/Qwen/Qwen2.5-72B-Instruct-AWQ`

    Args:
        model_path (_type_): _description_
    """
    config_path = os.path.join(model_path, "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    config["rope_scaling"] = {
            "factor": 4.0,
            "original_max_position_embeddings": 32768,
            "type": "yarn"
        }
    with open(config_path, "w") as f:
        json.dump(config,f,ensure_ascii=False,indent=2)


def replace_chat_template_hook(model_path,**kwargs):
    """Add prefill template to llama3d3_chat_template model.

    Args:
        model_path (_type_): _description_
    """
    tokenizer_path = os.path.join(model_path, "tokenizer_config.json")
    with open(tokenizer_path, "r") as f:
        tokenizer_config = json.load(f)

    chat_template_path = kwargs['chat_template']
    with open(chat_template_path, "r") as f:
        chat_template = f.read()

    tokenizer_config['chat_template'] = chat_template
    with open(tokenizer_path, "w") as f:
        json.dump(tokenizer_config,f,ensure_ascii=False,indent=2)
