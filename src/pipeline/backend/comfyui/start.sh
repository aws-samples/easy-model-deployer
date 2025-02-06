#!/bin/bash

#set -euxo pipefail

arch

# -------------------- common init --------------------

# Use verified cache version file for production: v1.5.0-fe21616
export CACHE_PUBLIC_COMFY="aws-gcr-solutions-us-east-1/stable-diffusion-aws-extension-github-mainline/dev/comfy.tar"

export ENDPOINT_INSTANCE_ID=$(date +"%m%d%H%M%S")

cores=$(lscpu | grep "^Core(s) per socket:" | awk '{print $4}')
sockets=$(lscpu | grep "^Socket(s):" | awk '{print $2}')
export CUP_CORE_NUMS=$((cores * sockets))

echo "---------------------------------------------------------------------------------"
echo "whoami: $(whoami)"
echo "Current shell: $SHELL"
echo "Running in $(bash --version)"
echo "---------------------------------------------------------------------------------"
echo "CREATED_AT: $CREATED_AT"
created_time_seconds=$(date -d "$CREATED_AT" +%s)
current_time=$(date "+%Y-%m-%dT%H:%M:%S.%6N")
current_time_seconds=$(date -d "$current_time" +%s)
export INSTANCE_INIT_SECONDS=$(( current_time_seconds - created_time_seconds ))
echo "NOW_AT: $current_time"
echo "Init from Create: $INSTANCE_INIT_SECONDS seconds"
echo "---------------------------------------------------------------------------------"
printenv
echo "---------------------------------------------------------------------------------"
nvidia-smi
echo "---------------------------------------------------------------------------------"
df -h
echo "---------------------------------------------------------------------------------"

# -------------------- common functions --------------------

set_conda(){
    echo "set conda environment..."
    export LD_LIBRARY_PATH=/home/ubuntu/conda/lib:$LD_LIBRARY_PATH
}

comfy_launch(){
  echo "---------------------------------------------------------------------------------"
  echo "accelerate comfy launch..."

  set_conda

  cd ComfyUI || exit 1
  chmod -R +x venv/bin

  source venv/bin/activate

  python main.py --listen
}

comfy_launch
