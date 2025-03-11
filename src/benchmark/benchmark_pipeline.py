import asyncio
import os
import argparse

os.environ["BASE_URL"] = "http://localhost:8080"
os.environ["SYSTEM_PROMPT"] = "1"
os.environ["MAX_TOKENS"] = "2048"
os.environ["MIN_TOKENS"] = "2048"
# os.environ["MODEL_ID"] = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
# os.environ["MODEL_ID"] = "DeepSeek-R1-Distill-Qwen-32B"
os.environ["MODEL_ID"] = "Qwen2.5-72B-Instruct-AWQ"
os.environ["PROMPT_FILE"] = "short_prompts.txt"

from benchmark import (OpenAIUserDef, OpenAIStreamUserDef)
from common import start_benchmark_session

session_time = 300
ping_correction = True
max_users_list = [1, 5, 10, 20, 40, 80]
# max_users_list = [80]
# max_users_list = [20]

for max_users in max_users_list:
    args = argparse.Namespace(max_users=max_users, session_time=session_time, ping_correction=ping_correction)
    asyncio.run(start_benchmark_session(args, OpenAIStreamUserDef))
    print(f"Stream Benchmarking with {max_users} users completed.")
    # asyncio.run(start_benchmark_session(args, OpenAIUserDef))
    # print(f"Benchmarking with {max_users} users completed.")
