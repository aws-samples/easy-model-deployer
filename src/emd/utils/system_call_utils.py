import subprocess

def execute_command(shell_script:str) -> subprocess.CompletedProcess:
    result = subprocess.run(
        shell_script,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    return result
