from .system_call_utils import execute_command
import os
import json


def get_gpu_num(shell_script="nvidia-smi --list-gpus | wc -l"):
    ret = execute_command(shell_script)
    if ret.returncode != 0:
        raise RuntimeError(f"Failed to get gpu num: \n{ret.stderr}")

    stdout = ret.stdout.decode("utf-8").strip()
    try:
        gpu_num = int(stdout)
        return gpu_num
    except ValueError:
        raise ValueError(f"Failed to parse gpu nums: {stdout}")


def get_neuron_core_num(shell_script="neuron-ls -j"):
    ret = execute_command(shell_script)
    if ret.returncode != 0:
        raise RuntimeError(f"Failed to get neuron core num: \n{ret.stderr}")
    stdout = ret.stdout.decode("utf-8").strip()
    core_num = len(json.loads(stdout))
    return core_num



def command_exists(command):
    return os.system(f"command -v {command} > /dev/null 2>&1") == 0


def check_neuron_exists():
    return command_exists("neuron-ls")

def check_cuda_exists():
    return command_exists("nvidia-smi")
