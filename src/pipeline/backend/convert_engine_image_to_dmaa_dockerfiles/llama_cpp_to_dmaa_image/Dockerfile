ARG CUDA_IMAGE="12.4.0-devel-ubuntu22.04"
FROM nvidia/cuda:${CUDA_IMAGE}

# We need to set the host to 0.0.0.0 to allow outside access
ENV HOST=0.0.0.0

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y zip unzip curl wget git build-essential \
    python3 python3-pip gcc wget \
    ocl-icd-opencl-dev opencl-headers clinfo \
    libclblast-dev libopenblas-dev \
    && mkdir -p /etc/OpenCL/vendors && echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd


# setting build related env vars
ENV CUDA_DOCKER_ARCH=all
ENV GGML_CUDA=1

# Install depencencies
# RUN python3 -m pip install --upgrade pip pytest cmake scikit-build setuptools fastapi uvicorn sse-starlette pydantic-settings starlette-context

# Install llama-cpp-python (build with cuda)
# RUN CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python[server]


# RUN apt-get install build-essential cmake curl libcurl4-openssl-dev -y
# RUN cd /tmp && git clone https://github.com/ggerganov/llama.cpp
# RUN cd /tmp/llama.cpp && git reset --hard b9ab0a4d0b2ed19effec130921d05fb5c30b68c5
# RUN cd /tmp &&  cmake llama.cpp -B llama.cpp/build -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON -DLLAMA_CURL=ON
# RUN cd /tmp && cmake --build llama.cpp/build --config Release -j --clean-first --target llama-quantize llama-cli llama-gguf-split llama-server
# RUN cp /tmp/llama.cpp/build/bin/llama-* /tmp/llama.cpp


# execute in container, then commit the container
RUN apt-get update && apt-get install build-essential cmake curl libcurl4-openssl-dev -y
RUN git clone https://github.com/ggerganov/llama.cpp
RUN cd llama.cpp && git reset --hard b9ab0a4d0b2ed19effec130921d05fb5c30b68c5
RUN cmake llama.cpp -B llama.cpp/build -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON -DLLAMA_CURL=ON && cmake --build llama.cpp/build --config Release -j --clean-first --target llama-quantize llama-cli llama-gguf-split llama-server
RUN cp llama.cpp/build/bin/llama-* llama.cpp


ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/tmp/llama.cpp

RUN python3 -m pip  install boto3 huggingface_hub ipython hf_transfer openai fastapi uvicorn
RUN mkdir -p /opt/ml/code
RUN mkdir -p /opt/ml/code/emd_models

RUN ln -s /tmp/llama.cpp/llama-server /opt/ml/code/llama-server

RUN curl https://github.com/peak/s5cmd/releases/download/v2.0.0/s5cmd_2.0.0_Linux-64bit.tar.gz -L -o /tmp/s5cmd.tar.gz
RUN mkdir -p /tmp/s5cmd && tar -xvf /tmp/s5cmd.tar.gz -C /tmp/s5cmd
RUN cp /tmp/s5cmd/s5cmd /opt/ml/code

WORKDIR /opt/ml/code

# COPY ./Dockerfile /
# Run the server
# CMD python3 -m llama_cpp.server
ENTRYPOINT ["/bin/bash"]
