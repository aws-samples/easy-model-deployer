ARG CUDA_IMAGE="12.5.0-devel-ubuntu22.04"
FROM nvcr.io/nvidia/cuda:${CUDA_IMAGE}

ENV CUDA_HOME=/usr/local/cuda
ENV TORCH_CUDA_ARCH_LIST="8.6;8.9"

RUN apt-get update && apt-get upgrade -y && apt-get install git cmake curl -y
RUN curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -L -o /tmp/Miniconda3-latest-Linux-x86_64.sh
RUN bash /tmp/Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3
ENV PATH="/root/miniconda3/bin:${PATH}"

RUN mkdir -p /opt/ml/code
RUN mkdir -p /opt/ml/code/emd_models
RUN git clone https://github.com/kvcache-ai/ktransformers.git /opt/ml/code/ktransformers && cd /opt/ml/code/ktransformers && git checkout tags/v0.2.3

RUN conda install -c conda-forge libstdcxx-ng
RUN python -m venv /opt/ml/code/venv
RUN /bin/bash -c 'source /opt/ml/code/venv/bin/activate && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126'
RUN /bin/bash -c 'source /opt/ml/code/venv/bin/activate && pip install packaging ninja cpufeature numpy wheel openai'
RUN /bin/bash -c 'source /opt/ml/code/venv/bin/activate && pip install flash-attn==2.7.4.post1 --no-build-isolation'
RUN /bin/bash -c 'source /opt/ml/code/venv/bin/activate && pip install flashinfer-python==0.2.3'
RUN /bin/bash -c 'source /opt/ml/code/venv/bin/activate && cd /opt/ml/code/ktransformers && git submodule init && git submodule update'

COPY backend/ktransformers/DeepSeek-R1/ /opt/ml/model/DeepSeek-R1

# Download and extract tokenizer.zip
RUN curl -L -o /tmp/tokenizer.zip https://aws-gcr-solutions-us-east-1.s3.us-east-1.amazonaws.com/easy-model-deployer/pipeline/ktransformers/tokenizer.zip && \
    cd /opt/ml/model/DeepSeek-R1 && \
    unzip -o /tmp/tokenizer.zip && \
    rm /tmp/tokenizer.zip

RUN pip install fastapi uvicorn requests

EXPOSE 8080
WORKDIR /opt/ml/code
