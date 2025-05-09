from typing import Annotated

import typer
from emd.constants import MODEL_DEFAULT_TAG
from emd.models.model import Model
from emd.models.utils.constants import ModelType
from emd.sdk.status import get_model_status
from emd.utils.decorators import catch_aws_credential_errors, check_emd_env_exist, load_aws_profile
from rich.console import Console
from rich.table import Table

app = typer.Typer(pretty_exceptions_enable=False)
console = Console()


@app.callback(invoke_without_command=True)
@catch_aws_credential_errors
@check_emd_env_exist
@load_aws_profile
def example(
    model_id_with_tag: Annotated[
        str, typer.Argument(help="MODEL_ID/MODEL_TAG"),
    ],
):
    """
    Generate example API calls for the specified model.
    """
    # Parse model_id and model_tag from the input
    if "/" in model_id_with_tag:
        model_id, model_tag = model_id_with_tag.split("/", 1)
    else:
        model_id = model_id_with_tag
        model_tag = MODEL_DEFAULT_TAG

    # Get model status to retrieve base URL
    ret = get_model_status(model_id, model_tag=model_tag)
    inprogress = ret['inprogress']
    completed = ret['completed']

    # Extract base URL from model outputs
    base_url = None
    for model_data in completed + inprogress:
        try:
            outputs = model_data.get('outputs', '')
            if outputs and isinstance(outputs, str) and '{' in outputs:
                import ast
                outputs_dict = ast.literal_eval(outputs)
                if isinstance(outputs_dict, dict) and "BaseURL" in outputs_dict:
                    base_url = outputs_dict["BaseURL"]
                    break
        except (SyntaxError, ValueError):
            continue

    if not base_url:
        console.print("[bold red]No deployed model found with a base URL.[/bold red]")
        return

    # Get model type
    try:
        model = Model.get_model(model_id)
        model_type = model.model_type
    except KeyError:
        console.print(f"[bold red]Model ID '{model_id}' is not supported.[/bold red]")
        return

    # Generate example based on model type
    if model_type == ModelType.LLM:
        _generate_chat_completion_example(base_url, model_id, model_tag)
    elif model_type == ModelType.VLM:
        _generate_vision_example(base_url, model_id, model_tag)
    elif model_type == ModelType.EMBEDDING:
        _generate_embedding_example(base_url, model_id, model_tag)
    elif model_type == ModelType.ASR:
        _generate_asr_example(base_url, model_id, model_tag)
    else:
        # Default to chat completion example
        _generate_chat_completion_example(base_url, model_id, model_tag)


def _generate_chat_completion_example(base_url, model_id, model_tag):
    """Generate example for chat completion models"""
    # Always include the tag in the example payload
    full_model_id = f"{model_id}/{model_tag}"

    curl_example = f"""curl {base_url}/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer <API Key>" \\
  -d '{{
        "model": "{full_model_id}",
        "messages": [
          {{"role": "system", "content": "You are a helpful assistant."}},
          {{"role": "user", "content": "Hello!"}}
        ],
        "stream": false
      }}'"""

    console.print("\n[bold]Create Chat Completion[/bold]")

    # Create a simple table for POST and URL
    table = Table(show_header=False, box=None)
    table.add_column(style="bold")
    table.add_column(overflow="fold")
    table.add_row("POST", f"{base_url}/v1/chat/completions")
    console.print(table)

    console.print("\n[bold]Request Example[/bold]")

    # CURL example
    console.print("[bold]CURL[/bold]")
    console.print(curl_example)

    # Python example
    python_example = f"""# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key="<API Key>", base_url="{base_url}")

response = client.chat.completions.create(
    model="{full_model_id}",
    messages=[
        {{"role": "system", "content": "You are a helpful assistant"}},
        {{"role": "user", "content": "Hello"}},
    ],
    stream=False
)

print(response.choices[0].message.content)"""

    console.print("\n[bold]PYTHON[/bold]")
    console.print(python_example)


def _generate_vision_example(base_url, model_id, model_tag):
    """Generate example for vision models"""
    # Always include the tag in the example payload
    full_model_id = f"{model_id}/{model_tag}"

    curl_example = f"""curl {base_url}/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer <API Key>" \\
  -d '{{
        "model": "{full_model_id}",
        "messages": [
          {{
            "role": "user",
            "content": [
              {{
                "type": "text",
                "text": "What's in this image?"
              }},
              {{
                "type": "image_url",
                "image_url": {{
                  "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/..."
                }}
              }}
            ]
          }}
        ]
      }}'"""

    console.print("\n[bold]Create Vision Completion[/bold]")

    # Create a simple table for POST and URL
    table = Table(show_header=False, box=None)
    table.add_column(style="bold")
    table.add_column(overflow="fold")
    table.add_row("POST", f"{base_url}/v1/chat/completions")
    console.print(table)

    console.print("\n[bold]Request Example[/bold]")

    # CURL example
    console.print("[bold]CURL[/bold]")
    console.print(curl_example)

    # Python example
    python_example = f"""# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI
import base64

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "path/to/your/image.jpg"
base64_image = encode_image(image_path)

client = OpenAI(api_key="<API Key>", base_url="{base_url}")

response = client.chat.completions.create(
    model="{full_model_id}",
    messages=[
        {{
            "role": "user",
            "content": [
                {{"type": "text", "text": "What's in this image?"}},
                {{
                    "type": "image_url",
                    "image_url": {{
                        "url": f"data:image/jpeg;base64,{{base64_image}}"
                    }}
                }}
            ]
        }}
    ]
)

print(response.choices[0].message.content)"""

    console.print("\n[bold]PYTHON[/bold]")
    console.print(python_example)


def _generate_embedding_example(base_url, model_id, model_tag):
    """Generate example for embedding models"""
    # Always include the tag in the example payload
    full_model_id = f"{model_id}/{model_tag}"

    curl_example = f"""curl {base_url}/v1/embeddings \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer <API Key>" \\
  -d '{{
        "model": "{full_model_id}",
        "input": "The food was delicious and the service was excellent."
      }}'"""

    console.print("\n[bold]Create Embedding[/bold]")

    # Create a simple table for POST and URL
    table = Table(show_header=False, box=None)
    table.add_column(style="bold")
    table.add_column(overflow="fold")
    table.add_row("POST", f"{base_url}/v1/embeddings")
    console.print(table)

    console.print("\n[bold]Request Example[/bold]")

    # CURL example
    console.print("[bold]CURL[/bold]")
    console.print(curl_example)

    # Python example
    python_example = f"""# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key="<API Key>", base_url="{base_url}")

response = client.embeddings.create(
    model="{full_model_id}",
    input="The food was delicious and the service was excellent."
)

print(response.data[0].embedding)  # Vector representation of the input text
"""

    console.print("\n[bold]PYTHON[/bold]")
    console.print(python_example)


def _generate_asr_example(base_url, model_id, model_tag):
    """Generate example for ASR models"""
    # Always include the tag in the example payload
    full_model_id = f"{model_id}/{model_tag}"

    curl_example = f"""curl {base_url}/v1/audio/transcriptions \\
  -H "Authorization: Bearer <API Key>" \\
  -F file="@/path/to/audio.mp3" \\
  -F model="{full_model_id}"
"""

    console.print("\n[bold]Create Audio Transcription[/bold]")

    # Create a simple table for POST and URL
    table = Table(show_header=False, box=None)
    table.add_column(style="bold")
    table.add_column(overflow="fold")
    table.add_row("POST", f"{base_url}/v1/audio/transcriptions")
    console.print(table)

    console.print("\n[bold]Request Example[/bold]")

    # CURL example
    console.print("[bold]CURL[/bold]")
    console.print(curl_example)

    # Python example
    python_example = f"""# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key="<API Key>", base_url="{base_url}")

audio_file_path = "path/to/audio.mp3"
with open(audio_file_path, "rb") as audio_file:
    response = client.audio.transcriptions.create(
        model="{full_model_id}",
        file=audio_file
    )

print(response.text)  # Transcribed text
"""

    console.print("\n[bold]PYTHON[/bold]")
    console.print(python_example)


if __name__ == "__main__":
    example()
