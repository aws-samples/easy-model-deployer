from . import Engine
from .utils.constants import EngineType
from typing import Union

class OpenAICompitableEngine(Engine):
    api_key:Union[str,None] = None
    environment_variables:str = ""
    cli_args: str = ""
    default_cli_args: str = ""
    custom_gpu_num: Union[int,None] = None
    custom_neuron_core_num: Union[int,None] = None


class VllmEngine(OpenAICompitableEngine):
    pass


# class MultiModelVllmEngine:


class LMdeployEngine(OpenAICompitableEngine):
    pass


class TgiEngine(OpenAICompitableEngine):
    support_inf2_instance:bool = True
    compile_to_neuron:bool = False
    neuron_compile_params:Union[dict,None] = None
    entrypoint:str = "text-generation-launcher"


class LlamaCppEngine(OpenAICompitableEngine):
    pass


class OllamaEngine(OpenAICompitableEngine):
    pass

class HuggingFaceWhisperEngine(Engine):
    pass

class HuggingFaceLLMEngine(Engine):
    pretrained_model_init_kwargs: Union[dict,None] = None
    pretrained_tokenizer_init_kwargs: Union[dict,None] = None

class ComfyuiEngine(Engine):
    pass

class KtransformersEngine(OpenAICompitableEngine):
    pass

vllm_engine064 = VllmEngine(**{
            "engine_type":EngineType.VLLM,
            "engine_dockerfile_config": {"VERSION":"v0.6.4"},
            "engine_cls":"vllm.vllm_backend.VLLMBackend",
            "base_image_host":"public.ecr.aws",
            "use_public_ecr":True,
            "docker_login_region":"us-east-1",
            "default_cli_args": " --max_num_seq 10",
            # "environment_variables": "export VLLM_ATTENTION_BACKEND=FLASHINFER && export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
}
)

vllm_qwen2d5_engine064 = VllmEngine(**{
            **vllm_engine064.model_dump(),
            "default_cli_args": " --chat-template emd/models/chat_templates/qwen_2d5_add_prefill_chat_template.jinja --max_model_len 16000 --disable-log-stats --enable-auto-tool-choice --tool-call-parser hermes"
})


vllm_gemma3_engine = VllmEngine(
    **{
    **vllm_engine064.model_dump(),
    "engine_dockerfile_config": {"VERSION":"v7.4.0_gemma3"},
    "dockerfile_name":"Dockerfile_gemma3",
    "default_cli_args": " --max_num_seq 5 --max_model_len 20000",
    "environment_variables": "export VLLM_ATTENTION_BACKEND=FLASH_ATTN && export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
    }
)


vllm_texgemma082 = VllmEngine(**{
            "engine_type":EngineType.VLLM,
            "engine_dockerfile_config": {"VERSION":"v0.8.2"},
            "engine_cls":"vllm.vllm_backend.VLLMBackend",
            "base_image_host":"public.ecr.aws",
            "use_public_ecr":True,
            "docker_login_region":"us-east-1",
            "default_cli_args": " --max_num_seq 10 --disable-log-stats"
}
)


vllm_medgemma082 = VllmEngine(**{
            "engine_type":EngineType.VLLM,
            "engine_dockerfile_config": {"VERSION":"v0.8.2"},
            "engine_cls":"vllm.vllm_backend.VLLMBackend",
            "base_image_host":"public.ecr.aws",
            "use_public_ecr":True,
            "docker_login_region":"us-east-1",
            "default_cli_args": " --max_num_seq 10 --disable-log-stats"
}
)


vllm_mistral_small_engine082 = VllmEngine(
    **{
    **vllm_engine064.model_dump(),
    "engine_dockerfile_config": {"VERSION":"v0.8.2"},
    "dockerfile_name":"Dockerfile",
    "default_cli_args": " --tokenizer-mode mistral --config-format mistral --load-format mistral  --limit-mm-per-prompt 'image=4' --max-model-len 16384",
    "environment_variables": ""
    }
)

vllm_deepseek_r1_distill_qwen_engine071 = VllmEngine(**{
            **vllm_engine064.model_dump(),
            "engine_dockerfile_config": {"VERSION":"v0.7.1"},
            "default_cli_args": "--max_num_seq 256 --max_model_len 16000 --chat-template emd/models/chat_templates/deepseek_r1_distill.jinja"
})

vllm_deepseek_r1_distill_qwen_engine085 = VllmEngine(**{
            **vllm_engine064.model_dump(),
            "engine_dockerfile_config": {"VERSION":"v0.8.5"},
            "default_cli_args": "--max_num_seq 256 --max_model_len 16000 --chat-template emd/models/chat_templates/deepseek_r1_distill.jinja"
})


vllm_deepseek_r1_distill_llama_engine071 = vllm_deepseek_r1_distill_qwen_engine071

vllm_deepseek_r1_engine084 = VllmEngine(**{
            **vllm_engine064.model_dump(),
            "engine_dockerfile_config": {"VERSION":"v0.8.4"},
            "default_cli_args": "--max_num_seq 10 --max_model_len 16000 --chat-template emd/models/chat_templates/deepseek_r1.jinja"
})

vllm_qwen2d5_72b_engine064 = VllmEngine(**{
             **vllm_engine064.model_dump(),
            "default_cli_args": " --chat-template emd/models/chat_templates/qwen_2d5_add_prefill_chat_template.jinja --max_model_len 16000 --disable-log-stats --max_num_seq 10 --enable-auto-tool-choice --tool-call-parser hermes"
})


vllm_qwen2d5_128k_engine064 = VllmEngine(**{
            **vllm_engine064.model_dump(),
            "model_files_modify_hook": "emd.models.utils.model_files_modify_hooks.qwen2d5_128k_model_files_hook",
            "default_cli_args": " --chat-template emd/models/chat_templates/qwen_2d5_add_prefill_chat_template.jinja --gpu-memory-utilization 0.95 --max_model_len 120000 --max_num_seq 1 --disable-log-stats --enable-auto-tool-choice --tool-call-parser hermes"
})


vllm_qwen2vl7b_engine064 = VllmEngine(**{
             **vllm_engine064.model_dump(),
            "environment_variables": "export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
            "default_cli_args": " --chat-template emd/models/chat_templates/qwen2vl_add_prefill_chat_template.jinja --max_model_len 16000 --disable-log-stats --limit-mm-per-prompt image=2,video=1 --max_num_seq 1 --gpu_memory_utilization 0.9"
})


vllm_ui_tars_1_5_engin084 = VllmEngine(**{
             **vllm_engine064.model_dump(),
             "engine_dockerfile_config": {"VERSION":"v0.8.4"},
            "environment_variables": "export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
            "default_cli_args": " --max_model_len 16000 --disable-log-stats --limit-mm-per-prompt image=1,video=0 --max_num_seq 2 --gpu_memory_utilization 0.9 --enable-prefix-caching"
})



vllm_qwen3_engin084 = VllmEngine(**{
             **vllm_engine064.model_dump(),
             "engine_dockerfile_config": {"VERSION":"v0.8.5.dev649_g0189a65a2"},
            "environment_variables": "export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
            "default_cli_args": " --max_model_len 16000 --max_num_seq 30 --disable-log-stats  --enable-reasoning --reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser hermes --enable-prefix-caching"
})


vllm_qwen2vl72b_engine064 = VllmEngine(**{
             **vllm_engine064.model_dump(),
            "environment_variables": "export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
            "default_cli_args": " --chat-template emd/models/chat_templates/qwen2vl_add_prefill_chat_template.jinja --max_model_len 25000 --disable-log-stats --limit-mm-per-prompt image=20,video=1 --max_num_seq 1 --gpu_memory_utilization 0.9"
})

vllm_qwen25vl72b_engine073 = VllmEngine(**{
            **vllm_engine064.model_dump(),
            "engine_dockerfile_config": {"VERSION":"v0.7.3"},
            "dockerfile_name":"Dockerfile_qwen25_vl",
            "environment_variables": "export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
            "default_cli_args": " --max_model_len 25000 --disable-log-stats --limit-mm-per-prompt image=20,video=1 --max_num_seq 1 --gpu_memory_utilization 0.9"
})

vllm_qwen25vl72b_engine084 = VllmEngine(**{
            **vllm_engine064.model_dump(),
            "engine_dockerfile_config": {"VERSION":"v0.8.4"},
            "dockerfile_name":"Dockerfile_qwen25_vl",
            "environment_variables": "export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
            "default_cli_args": " --max_model_len 32000 --disable-log-stats --limit-mm-per-prompt image=1,video=1 --max_num_seq 1 --gpu_memory_utilization 0.7"
})

vllm_qwq_engine073 = VllmEngine(**{
            **vllm_qwen25vl72b_engine073.model_dump(),
            "environment_variables": "export VLLM_ATTENTION_BACKEND=FLASHINFER && export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
            "default_cli_args": " --chat-template emd/models/chat_templates/qwq_32b_add_prefill_chat_template.jinja --max_model_len 16000  --max_num_seq 10 --disable-log-stats --enable-auto-tool-choice --tool-call-parser hermes"
})

vllm_qwq_engine082 = VllmEngine(**{
            **vllm_qwen25vl72b_engine073.model_dump(),
            "engine_dockerfile_config": {"VERSION":"v0.8.2"},
            "environment_variables": "export VLLM_ATTENTION_BACKEND=FLASHINFER && export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
            "default_cli_args": " --chat-template emd/models/chat_templates/qwq_32b_add_prefill_chat_template.jinja --max_model_len 16000  --max_num_seq 10 --disable-log-stats --enable-auto-tool-choice --tool-call-parser hermes  --enable-reasoning --reasoning-parser deepseek_r1"
})


vllm_internvl2d5_76b_engine064 = VllmEngine(**{
             **vllm_engine064.model_dump(),
            "environment_variables": "export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
            "default_cli_args": " --chat-template emd/models/chat_templates/qwen2vl_add_prefill_chat_template.jinja --max_model_len 8192 --disable-log-stats --limit-mm-per-prompt image=5,video=1 --max_num_seq 1 --gpu_memory_utilization 0.9"
})



vllm_glm4_engine064 = vllm_engine064


vllm_glm4_0414_engine082 = VllmEngine(**{
            **vllm_qwen25vl72b_engine073.model_dump(),
            "engine_dockerfile_config": {"VERSION":"glm_z1_and_0414"},
            "environment_variables": "export VLLM_USE_V1=0 && export VLLM_ATTENTION_BACKEND=FLASHINFER && export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
            # "default_cli_args": "--max_model_len 16000  --max_num_seq 10 --disable-log-stats --enable-auto-tool-choice --tool-call-parser pythonic"
            "default_cli_args": "--max_model_len 16000  --max_num_seq 10 --disable-log-stats"
})


vllm_glm4_z1_engine082 = VllmEngine(**{
            **vllm_qwen25vl72b_engine073.model_dump(),
            "engine_dockerfile_config": {"VERSION":"glm_z1_and_0414"},
            "environment_variables": "export VLLM_USE_V1=0 && export VLLM_ATTENTION_BACKEND=FLASHINFER && export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
            # "default_cli_args": "--max_model_len 16000  --max_num_seq 10 --disable-log-stats --enable-auto-tool-choice --tool-call-parser pythonic --enable-reasoning --reasoning-parser granite"
            "default_cli_args": "--max_model_len 16000  --max_num_seq 10 --disable-log-stats --enable-reasoning --reasoning-parser granite"
})


vllm_glm4_wo_flashinfer_engine064 = VllmEngine(**{
             **vllm_engine064.model_dump(),
            #  "engine_dockerfile_config": {"VERSION":"v0.6.0"},
            "environment_variables": "",
            "default_cli_args": " --max_num_seq 10 --max_model_len 16000",
})


vllm_internlm2d5_engine064 = VllmEngine(
    **{
            **vllm_engine064.model_dump(),
            "default_cli_args": " --chat-template emd/models/chat_templates/internlm2d5_add_prefill_chat_template.jinja --max_model_len 16000 --disable-log-stats --enable-auto-tool-choice --tool-call-parser internlm"
    }
)

tgi_llama3d3_engine301 = TgiEngine(
    **{
        "engine_type":EngineType.TGI,
        "engine_dockerfile_config": {"VERSION":"3.0.1_modify_stop_seq_v2"},
        "engine_cls":"tgi.tgi_backend.TgiBackend",
        "base_image_host":"public.ecr.aws",
        "use_public_ecr":True,
        "docker_login_region":"us-east-1",
        "model_files_modify_hook":"emd.models.utils.model_files_modify_hooks.replace_chat_template_hook",
        "model_files_modify_hook_kwargs":{"chat_template":"emd/models/chat_templates/llama3d3_add_prefill_chat_templates.jinja"},
        "default_cli_args": " --max-total-tokens 16000 --max-concurrent-requests 10",
        # "environment_variables": "export VLLM_ATTENTION_BACKEND=FLASHINFER && export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
}
)

tgi_deepseek_r1_llama_70b_engine301 = TgiEngine(
    **{
        "engine_type":EngineType.TGI,
        "engine_dockerfile_config": {"VERSION":"3.0.1_modify_stop_seq_v2"},
        "engine_cls":"tgi.tgi_backend.TgiBackend",
        "base_image_host":"public.ecr.aws",
        "use_public_ecr":True,
        "docker_login_region":"us-east-1",
        "model_files_modify_hook":"emd.models.utils.model_files_modify_hooks.replace_chat_template_hook",
        "model_files_modify_hook_kwargs":{"chat_template":"emd/models/chat_templates/deepseek_r1_distill.jinja"},
        "default_cli_args": " --max-total-tokens 16000 --max-concurrent-requests 10",
        # "environment_variables": "export VLLM_ATTENTION_BACKEND=FLASHINFER && export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
        "environment_variables": "export PREFIX_CACHING=0"
}
)

ollama_deepseek_r1_qwen2d5_1d5b_engine057 = OllamaEngine(
    **{
        "engine_type":EngineType.OLLAMA,
        "engine_dockerfile_config": {"VERSION":"0.5.7_py312"},
        "engine_cls":"ollama.ollama_backend.OllamaBackend",
        "base_image_host":"public.ecr.aws",
        "use_public_ecr":True,
        "docker_login_region":"us-east-1",
    }
)

llama_cpp_deepseek_r1_1d58_bit_engine_b9ab0a4 = LlamaCppEngine(
    **{
        "engine_type":EngineType.LLAMA_CPP,
        "engine_dockerfile_config": {"VERSION":"b9ab0a4-cuda-12-4"},
        "engine_cls":"llama_cpp.llama_cpp_backend.LlamaCppBackend",
        "base_image_host":"public.ecr.aws",
        "use_public_ecr":True,
        "docker_login_region":"us-east-1",
        "default_cli_args":"--tensor-split 8,7,8,8,8,8,7,8  -ctk q4_0 --ctx-size 10240 --parallel 2 --batch-size 32 --threads 96 --prio 2 --temp 0.6 --top-p 0.95 --jinja --chat-template-file emd/models/chat_templates/deepseek_r1.jinja"
    }
)

llama_cpp_deepseek_r1_distill_engineb9ab0a4 = LlamaCppEngine(
    **{
        "engine_type":EngineType.LLAMA_CPP,
        "engine_dockerfile_config": {"VERSION":"b9ab0a4-cuda-12-4"},
        "engine_cls":"llama_cpp.llama_cpp_backend.LlamaCppBackend",
        "base_image_host":"public.ecr.aws",
        "use_public_ecr":True,
        "docker_login_region":"us-east-1",
        "default_cli_args":" -c 16000  -np 5 --temp 0.6  --jinja -ngl 10000 --cont-batching --threads-http 5 --chat-template-file emd/models/chat_templates/deepseek_r1_distill.jinja"
    }
)


tgi_qwen2d5_72b_engine064 = TgiEngine(
    **{
        "engine_type":EngineType.TGI,
        "engine_dockerfile_config": {"VERSION":"3.0.1_modify_stop_seq_v2"},
        "engine_cls":"tgi.tgi_backend.TgiBackend",
        "base_image_host":"public.ecr.aws",
        "use_public_ecr":True,
        "docker_login_region":"us-east-1",
        "model_files_modify_hook":"emd.models.utils.model_files_modify_hooks.replace_chat_template_hook",
        "model_files_modify_hook_kwargs": {"chat_template":"emd/models/chat_templates/qwen_2d5_add_prefill_chat_template.jinja"},
        "default_cli_args": " --max-total-tokens 16000 --max-concurrent-requests 10",
    }
)


tgi_llama3d3_60k_engine301 = TgiEngine(
    **{
        "engine_type":EngineType.TGI,
        "engine_dockerfile_config": {"VERSION":"3.0.1_modify_stop_seq_v2"},
        "engine_cls":"tgi.tgi_backend.TgiBackend",
        "base_image_host":"public.ecr.aws",
        "use_public_ecr":True,
        "docker_login_region":"us-east-1",
        "model_files_modify_hook":"emd.models.utils.model_files_modify_hooks.replace_chat_template_hook",
        "model_files_modify_hook_kwargs":{"chat_template":"emd/models/chat_templates/llama3d3_add_prefill_chat_templates.jinja"},
        "default_cli_args": " --max-total-tokens 60000 --max-concurrent-requests 1",
        # "environment_variables": "export VLLM_ATTENTION_BACKEND=FLASHINFER && export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
}
)

tgi_qwen2d5_on_inf2 = TgiEngine(
    **{
        "engine_type":EngineType.TGI,
        "engine_dockerfile_config": {"VERSION":"neuronx-tgi-0.0.28.dev0"},
        "engine_cls":"tgi.tgi_backend.TgiBackend",
        "base_image_host":"public.ecr.aws",
        "use_public_ecr":True,
        "docker_login_region":"us-east-1",
        "compile_to_neuron":True,
        "neuron_compile_params":{
            "num_cores":2,
            "auto_cast_type":'fp16',
            "batch_size":10,
            "sequence_length": 16000,
            "task":"text-generation"
        },
        "entrypoint": "/tgi-entrypoint.sh",
        "default_cli_args": " --max-batch-size 10 --max-input-tokens 15000",
    }
)

tgi_qwen2d5_72b_on_inf2 = TgiEngine(
    **{
        "engine_type":EngineType.TGI,
        "engine_dockerfile_config": {"VERSION":"neuronx-tgi-0.0.28.dev0"},
        "engine_cls":"tgi.tgi_backend.TgiBackend",
        "base_image_host":"public.ecr.aws",
        "use_public_ecr":True,
        "docker_login_region":"us-east-1",
        "compile_to_neuron":True,
        "neuron_compile_params":{
            "num_cores":8,
            "auto_cast_type":'fp16',
            "batch_size":10,
            "sequence_length": 16000,
            "task":"text-generation"
        },
        "entrypoint": "/tgi-entrypoint.sh",
        "default_cli_args": " --max-batch-size 10 --max-input-tokens 15000",
    }
)


# lmdeploy engine
lmdeploy_engine064 = LMdeployEngine(
    **{
    "engine_type":EngineType.LMDEPLOY,
    "engine_dockerfile_config": {"VERSION":"v0.6.4-cu12"},
    "engine_cls":"lmdeploy.lmdeploy_backend.LMdeployBackend",
    "base_image_host":"public.ecr.aws",
    "use_public_ecr":True,
    "docker_login_region":"us-east-1",
    "default_cli_args": " --max-batch-size 1"
    }
)

lmdeploy_intervl2d5_awq_engine064 = LMdeployEngine(
    **{
        **lmdeploy_engine064.model_dump(),
        "dockerfile_name":"Dockerfile_internvl2",
        "default_cli_args":" --max-batch-size 1 --backend turbomind --model-format awq"
    }
)


vllm_M1_14B_engine066 = VllmEngine(**{
            "engine_type":EngineType.VLLM,
            "engine_dockerfile_config": {"VERSION":"v0.6.6-baichuan-m1"},
            "engine_cls":"vllm.vllm_backend.VLLMBackend",
            "base_image_host":"public.ecr.aws",
            "use_public_ecr":True,
            "docker_login_region":"us-east-1",
            "custom_gpu_num":2,
            "default_cli_args": " --disable-log-stats --trust-remote-code"
})



vllm_embedding_engine064 = VllmEngine(**{
            "engine_type":EngineType.VLLM,
            "engine_dockerfile_config": {"VERSION":"v0.6.4"},
            "engine_cls":"vllm.vllm_backend.VLLMBackend",
            "base_image_host":"public.ecr.aws",
            "use_public_ecr":True,
            "docker_login_region":"us-east-1",
            "default_cli_args": " --max_num_seq 30 --disable-log-stats"
})

vllm_embedding_engine066 = VllmEngine(**{
            "engine_type":EngineType.VLLM,
            "engine_dockerfile_config": {"VERSION":"v0.6.6"},
            "engine_cls":"vllm.vllm_backend.VLLMBackend",
            "base_image_host":"public.ecr.aws",
            "use_public_ecr":True,
            "docker_login_region":"us-east-1",
            "default_cli_args": " --disable-log-stats"
})


huggingface_whisper_engine = HuggingFaceWhisperEngine(**{
            "engine_type":EngineType.HUGGINGFACE,
            "engine_cls":"huggingface.whisper.whisper_backend.WhisperBackend",
            "base_image_account_id":"763104351884",
            "python_name":"python"
})


huggingface_llm_engine_4d41d2 = HuggingFaceLLMEngine(**{
            "engine_type":EngineType.HUGGINGFACE,
            "engine_cls":"huggingface.llm.transformer_llm_backend.TransformerLLMBackend",
            "python_name":"python3",
            "base_image_host":"public.ecr.aws",
            "use_public_ecr":True,
            "docker_login_region":"us-east-1",
            "engine_dockerfile_config": {"VERSION":"4.41.2"},
})

huggingface_baichuan_engine_4d41d2 = HuggingFaceLLMEngine(**{
            "engine_type":EngineType.HUGGINGFACE,
            "engine_cls":"huggingface.llm.transformer_llm_backend.TransformerLLMBackend",
            "python_name":"python3",
            "base_image_host":"public.ecr.aws",
            "use_public_ecr":True,
            "docker_login_region":"us-east-1",
            "dockerfile_name":"Dockerfile_baichuan",
            "engine_dockerfile_config": {"VERSION":"4.49.0"},
            "pretrained_model_init_kwargs":{"trust_remote_code":True},
            "pretrained_tokenizer_init_kwargs":{"trust_remote_code":True}
})

huggingface_embedding_engine449 = HuggingFaceLLMEngine(**{
            "engine_type":EngineType.HUGGINGFACE,
            "engine_cls":"huggingface.embedding.transformers_embedding_backend.TransformerEmbeddingBackend",
            "python_name":"python3",
            "base_image_host":"public.ecr.aws",
            "use_public_ecr":True,
            "docker_login_region":"us-east-1",
            "engine_dockerfile_config": {"VERSION":"4.49.0"},
            "pretrained_model_init_kwargs":{"trust_remote_code":True,"torch_dtype":"float16"},
})

huggingface_rerank_engine449 = HuggingFaceLLMEngine(**{
            "engine_type":EngineType.HUGGINGFACE,
            "engine_cls":"huggingface.rerank.transformers_rerank_backend.TransformerRerankBackend",
            "python_name":"python3",
            "base_image_host":"public.ecr.aws",
            "use_public_ecr":True,
            "docker_login_region":"us-east-1",
            "engine_dockerfile_config": {"VERSION":"4.49.0"},
            "pretrained_model_init_kwargs":{"trust_remote_code":True,"torch_dtype":"float16"},
})

comfyui_engine = ComfyuiEngine(**{
            "engine_type":EngineType.COMFYUI,
            "engine_cls":"comfyui.comfyui_backend.ComfyUIBackend",
            "base_image_host":"public.ecr.aws",
            "use_public_ecr":True,
            "docker_login_region":"us-east-1",
})

ktransformers_engine = KtransformersEngine(**{
            "engine_type":EngineType.KTRANFORMERS,
            "engine_cls":"ktransformers.ktransformers_backend.KTransformersBackend",
            "base_image_host":"nvcr.io",
            "use_public_ecr":False,
            "default_cli_args": " --max_new_tokens 2048",
})

custom_engine = Engine(**{
            "engine_type":EngineType.CUSTOM,
})
