
FROM public.ecr.aws/aws-gcr-solutions/nvidia/cuda:12.2.0-base-ubuntu22.04
#FROM public.ecr.aws/ubuntu/ubuntu:22.04_stable

SHELL ["/bin/bash", "-c"]

WORKDIR /home/ubuntu/

RUN adduser --disabled-password --gecos '' ubuntu && \
    apt-get update -y && \
    apt-get install --no-install-recommends -y \
                    git libgl1 libtcmalloc-minimal4 libglib2.0-0 python3.10 python3.10-venv net-tools bc \
                    pkg-config file curl protobuf-compiler mesa-utils \
                    python3-dev libaio-dev libcairo2-dev libprotobuf-dev build-essential cmake wget ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    wget -q https://github.com/peak/s5cmd/releases/download/v2.2.2/s5cmd_2.2.2_Linux-64bit.tar.gz && \
    tar xzvf s5cmd_2.2.2_Linux-64bit.tar.gz && \
    rm -rf s5cmd_2.2.2_Linux-64bit.tar.gz && \
    mv s5cmd /usr/local/bin/


ENV ESD_COMMIT_ID=dev
ENV ON_SAGEMAKER true
ENV LD_PRELOAD /usr/lib/x86_64-linux-gnu/libtcmalloc_minimal.so.4

RUN mkdir -p /home/ubuntu/conda/lib/ && \
    wget -qO /home/ubuntu/conda/lib/libcufft.so.10 https://huggingface.co/elonniu/esd/resolve/main/libcufft.so.10 && \
    wget -qO /home/ubuntu/conda/lib/libcurand.so.10 https://huggingface.co/elonniu/esd/resolve/main/libcurand.so.10

COPY backend/comfyui/install_comfy.sh /home/ubuntu/
#COPY trim_comfy.sh /home/ubuntu/

COPY backend/comfyui/start.sh /
RUN chmod +x /start.sh


RUN cd /home/ubuntu || exit 1 && \
    bash install_comfy.sh


# RUN mkdir -p /home/ubuntu/ComfyUI/models/vae/
# RUN mkdir -p /home/ubuntu/ComfyUI/models/animatediff_models/

# RUN wget -qO '/home/ubuntu/ComfyUI/models/vae/vae-ft-mse-840000-ema-pruned.safetensors' 'https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors'
# RUN wget -qO '/home/ubuntu/ComfyUI/models/animatediff_models/v3_sd15_mm.ckpt' 'https://huggingface.co/guoyww/animatediff/resolve/main/v3_sd15_mm.ckpt'
# RUN wget -qO '/home/ubuntu/ComfyUI/models/checkpoints/DreamShaper_7_pruned.safetensors' 'https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_7_pruned.safetensors'

# COPY src /home/ubuntu/src
# COPY src/deploy/on_sagemaker/serve /usr/bin/serve
# RUN chmod +x /usr/bin/serve
RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip install uvicorn
RUN pip install fastapi
RUN pip install requests
RUN pip install boto3
RUN pip install aiohttp
RUN pip install websocket
RUN pip install websocket-client
# Set the serve script as the entrypoint
ENTRYPOINT ["/usr/bin/serve"]