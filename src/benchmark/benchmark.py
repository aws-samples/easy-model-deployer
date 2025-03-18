import argparse
import functools
import random
import os
import json
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from transformers import AutoTokenizer

from userdef import UserDef as BaseUserDef

model_id = os.environ.get("MODEL_ID", "Qwen2.5-7B-Instruct")

try:
    max_tokens = int(os.environ.get("MAX_TOKENS"))
except (TypeError, ValueError):
    max_tokens = 512

try:
    min_tokens = int(os.environ.get("MIN_TOKENS"))
except (TypeError, ValueError):
    min_tokens = 0

print(f"max_tokens set to {max_tokens}")

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")

default_system_prompt = """You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."""

if os.environ.get("SYSTEM_PROMPT") == "1":
    system_prompt = default_system_prompt
    system_prompt_file = os.environ.get("SYSTEM_PROMPT_FILE")
    if system_prompt_file is not None:
        with open(system_prompt_file) as f:
            system_prompt = f.read().strip()
else:
    system_prompt = ""

base_url = os.environ.get("BASE_URL", "http://localhost:3000")


@functools.lru_cache(maxsize=8)
def get_prompt_set(min_input_length=0, max_input_length=500):
    """
    return a list of prompts with length between min_input_length and max_input_length
    """
    import json
    import requests
    import os

    # check if the dataset is cached
    if os.path.exists("databricks-dolly-15k.jsonl"):
        print("Loading cached dataset")
        with open("databricks-dolly-15k.jsonl", "r") as f:
            dataset = [json.loads(line) for line in f.readlines()]
    else:
        print("Downloading dataset")
        raw_dataset = requests.get(
            "https://huggingface.co/datasets/databricks/databricks-dolly-15k/resolve/main/databricks-dolly-15k.jsonl"
        )
        content = raw_dataset.content
        open("databricks-dolly-15k.jsonl", "wb").write(content)
        dataset = [json.loads(line) for line in content.decode().split("\n")]
        print("Dataset downloaded")

    for d in dataset:
        d["question"] = d["context"] + d["instruction"]
        d["input_tokens"] = len(tokenizer(d["question"])["input_ids"])
        d["output_tokens"] = len(tokenizer(d["response"]))
    return [
        d["question"]
        for d in dataset
        if min_input_length <= d["input_tokens"] <= max_input_length
    ]

# prompts = get_prompt_set(30, 150)
user_prompt_file = os.environ.get("PROMPT_FILE")
with open(user_prompt_file, "r") as f:
    prompt = f.read()
    print(f"The tokens of the prompt is {len(tokenizer(prompt)['input_ids'])}")
prompts = [prompt]


class OpenAIUserDef(BaseUserDef):
    # Alias endpoint and query inputs for readability
    BASE_URL = base_url
    PROMPTS = prompts

    @classmethod
    def make_request(cls):
        # Move imports inside method for performance
        from random import sample
        import json as json_parser

        # Select a random prompt from our collection
        selected_prompt = random.choice(cls.PROMPTS)

        # Prepare HTTP request components
        request_metadata = {"Content-Type": "application/json"}
        endpoint = f"{cls.BASE_URL}/v1/chat/completions"

        # Build the payload with necessary parameters
        payload = {
            "messages": [{
                "role": "system",
                "content": system_prompt
            }, {
                "role": "user",
                "content": selected_prompt
            }],
            "model": model_id,
            "max_tokens": max_tokens,
            "stream": False,
            "extra_body": {
                "min_tokens": min_tokens,
            }
        }

        # Return request components in expected format
        return endpoint, request_metadata, json_parser.dumps(payload)

    @staticmethod
    def parse_response(response_bytes: bytes):
        # Process the raw bytes from model response
        decoded_content = response_bytes.decode("utf-8").strip()
        data = json.loads(decoded_content)
        content = data.get("choices")[0].get("message").get("content")
        print(f"The content length is {len(content)}")
        print(f"The tokens of the content is {len(tokenizer(content)['input_ids'])}")
        last_token_id = tokenizer(content)["input_ids"][-1]
        last_token = tokenizer.decode(last_token_id)
        print(f"The last token id of the content is {last_token}")

        # Convert text to token IDs for benchmarking
        return tokenizer.encode(content, add_special_tokens=False)

class OpenAIStreamUserDef(BaseUserDef):
    # Alias endpoint and query inputs for readability
    BASE_URL = base_url
    PROMPTS = prompts

    @classmethod
    def make_request(cls):
        # Move imports inside method for performance
        from random import sample
        import json as json_parser

        # Select a random prompt from our collection
        selected_prompt = random.choice(cls.PROMPTS)

        # Prepare HTTP request components
        request_metadata = {"Content-Type": "application/json"}
        endpoint = f"{cls.BASE_URL}/v1/chat/completions"

        # Build the payload with necessary parameters
        payload = {
            "messages": [{
                "role": "system",
                "content": system_prompt
            }, {
                "role": "user",
                "content": selected_prompt
            }],
            "model": model_id,
            "max_tokens": max_tokens,
            "stream": True,
            "extra_body": {
                "min_tokens": min_tokens,
            }
        }

        # Return request components in expected format
        return endpoint, request_metadata, json_parser.dumps(payload)

    @staticmethod
    def parse_response(response_bytes: bytes):
        # Process the raw bytes from model response
        decoded_content = response_bytes.decode("utf-8").strip()
        try:
            data = json.loads(decoded_content[6:])
            content = data.get("choices")[0].get("delta").get("content")
            if content is None:
                content = ""
        except Exception as e:
            logger.error(f"Failed to decode content: {decoded_content}")
            content = ""

        # Convert text to token IDs for benchmarking
        return tokenizer.encode(content, add_special_tokens=False)

if __name__ == "__main__":
    import asyncio
    from common import start_benchmark_session

    # arg parsing
    parser = argparse.ArgumentParser(description="Benchmark")
    parser.add_argument("--max_users", type=int, required=True)
    parser.add_argument("--session_time", type=float, default=None)
    parser.add_argument("--ping_correction", action="store_true")
    args = parser.parse_args()

    asyncio.run(start_benchmark_session(args, OpenAIStreamUserDef))
