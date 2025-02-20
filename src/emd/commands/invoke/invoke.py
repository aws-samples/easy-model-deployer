import typer
from rich.console import Console
from typing import Optional
from typing_extensions import Annotated

from rich.prompt import Prompt

from emd.constants import MODEL_DEFAULT_TAG
from emd.models import Model
from emd.models.utils.constants import ModelType
from emd.utils.logger_utils import make_layout
from emd.utils.decorators import catch_aws_credential_errors,check_emd_env_exist,load_aws_profile

app = typer.Typer()
console = Console()
layout = make_layout()


def conversation_invoke(model_id:str,model_tag):
    model = Model.get_model(model_id)
    from emd.sdk.invoke.conversation_invoker import ConversationInvoker
    invoker = ConversationInvoker(model_id,model_tag)
    while True:
        user_message = Prompt.ask("[bold yellow]Write a prompt, press Enter to generate a response (Ctrl+C to abort), \nUser[/bold yellow]")
        # user_message = typer.prompt(
        #     "[bold yellow]Write a prompt, press Enter to generate a response (Ctrl+C to abort), User[/bold yellow]"
        # )
        if user_message == "exit":
            break
        if not user_message:
            continue
        invoker.add_user_message(user_message)
        ai_message:str = invoker.invoke()
        # content = ai_message['content']
        # reasoning_content = ai_message.get('reasoning_content','')
        # if reasoning_content:
        #     content = f"<think>\n{reasoning_content}\n</think>\n{content}"
        console.print(f"[bold green]Assistant:{ai_message}[/bold green]")
        invoker.add_assistant_message(ai_message)

def whisper_invoke(model_id,model_tag):
    model = Model.get_model(model_id)
    from emd.sdk.invoke.whisper_invoker import WhisperInvoker
    invoker = WhisperInvoker(model_id, model_tag)

    audio_input = Prompt.ask("[bold yellow]Enter the s3 path to the audio file[/bold yellow]")
    invoker.add_audio_input(audio_input)
    model = Prompt.ask(
        "[bold yellow]Enter model[/bold yellow]",
        choices=["large-v3-turbo", "large-v3"]
    )
    invoker.add_model(model)

    ret = invoker.invoke()
    console.print(f"[bold green]Outputs: {ret}[/bold green]")


def embedding_invoke(model_id,model_tag):
    model = Model.get_model(model_id)
    from emd.sdk.invoke.embedding_invoker import EmbeddingInvoker
    invoker = EmbeddingInvoker(model_id, model_tag)

    input = Prompt.ask("[bold yellow]Enter the sentence[/bold yellow]")
    invoker.add_input(input)
    ret = invoker.invoke()
    console.print(f"[bold green]Outputs: {ret}[/bold green]")

def rerank_invoke(model_id, model_tag):
    model = Model.get_model(model_id)
    from emd.sdk.invoke.rerank_invoker import RerankInvoker
    invoker = RerankInvoker(model_id, model_tag)
    text_a = Prompt.ask("[bold yellow]Enter the text_a (string)[/bold yellow]")
    invoker.add_text_a(text_a)
    text_b = Prompt.ask("[bold yellow]Enter the text_b (string)[/bold yellow]")
    invoker.add_text_b(text_b)
    ret = invoker.invoke()
    console.print(f"[bold green]Outputs: {ret}[/bold green]")


def gen_video_invoke(model_id,model_tag):
    from emd.sdk.invoke.comfyui_invoke import ComfyUIInvoker
    invoker = ComfyUIInvoker(model_id, model_tag)

    input = Prompt.ask("[bold yellow]Enter a prompt to generate a video[/bold yellow]")
    invoker.add_input(input)
    ret = invoker.invoke()
    console.print(f"[bold green]Outputs: {ret}[/bold green]")

def vlm_invoke(model_id,model_tag):
    from emd.sdk.invoke.vlm_invoker import VLMInvoker
    invoker = VLMInvoker(model_id, model_tag)
    image_path = Prompt.ask("[bold yellow]Enter image path (local or s3 file)[/bold yellow]")
    invoker.add_image(image_path)
    prompt = Prompt.ask("[bold yellow]Enter prompt[/bold yellow]")
    invoker.add_user_message(prompt)
    ret = invoker.invoke()
    console.print(f"[bold green]Outputs: {ret}[/bold green]")


@app.callback(invoke_without_command=True)
@catch_aws_credential_errors
@check_emd_env_exist
@load_aws_profile
def invoke(
    model_id: Annotated[str, typer.Argument(help="Model ID")],
    model_tag: Annotated[str, typer.Argument(help="Model rag")] = MODEL_DEFAULT_TAG
    ):
    console.print(f"Invoking model {model_id} with tag {model_tag}")
    model:Model = Model.get_model(model_id)
    model_type = model.model_type
    if model_type == ModelType.LLM:
        return conversation_invoke(model_id,model_tag)
    elif model_type == ModelType.WHISPER:
        return whisper_invoke(model_id, model_tag)
    elif model_type == ModelType.EMBEDDING:
        return embedding_invoke(model_id, model_tag)
    elif model_type == ModelType.VLM:
        return vlm_invoke(model_id, model_tag)
    elif model_type == ModelType.RERANK:
        return rerank_invoke(model_id, model_tag)
    elif model_type == ModelType.VIDEO:
        return gen_video_invoke(model_id, model_tag)
    else:
        raise NotImplementedError

import sys
if __name__ == "__main__":
    invoke(sys.argv[1])
