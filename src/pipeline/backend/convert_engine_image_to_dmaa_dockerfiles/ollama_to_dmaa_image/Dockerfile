FROM ollama/ollama:0.5.7

# 安装构建依赖
RUN apt update && apt install -y \
    build-essential \
    zlib1g-dev \
    libssl-dev \
    libreadline-dev \
    libsqlite3-dev \
    zip \
    unzip \
    wget \
    curl \
    libbz2-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 下载并编译 Python 3.12
RUN wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz \
    && tar -xf Python-3.12.0.tgz \
    && cd Python-3.12.0 \
    && ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make altinstall \
    && cd .. \
    && rm -rf Python-3.12.0 Python-3.12.0.tgz

# 检查 Python 版本
RUN python3.12 --version
RUN ln -s  /usr/local/bin/python3.12 /usr/local/bin/python
RUN ln -s  /usr/local/bin/python3.12 /usr/local/bin/python3
RUN ln -s  /usr/local/bin/pip3.12 /usr/local/bin/pip
RUN ln -s  /usr/local/bin/pip3.12 /usr/local/bin/pip3

RUN pip3 install boto3 huggingface_hub ipython hf_transfer

RUN mkdir -p /opt/ml/code
RUN mkdir -p /opt/ml/code/emd_models
COPY ./Dockerfile /

RUN curl https://github.com/peak/s5cmd/releases/download/v2.0.0/s5cmd_2.0.0_Linux-64bit.tar.gz -L -o /tmp/s5cmd.tar.gz
RUN mkdir -p /tmp/s5cmd && tar -xvf /tmp/s5cmd.tar.gz -C /tmp/s5cmd
RUN cp /tmp/s5cmd/s5cmd /opt/ml/code


# RUN apt update && apt install -y git build-essential cmake curl libcurl4-openssl-dev
# RUN apt update && apt install -y nvidia-cuda-toolkit
# RUN git clone https://github.com/ggerganov/llama.cpp /tmp/llama.cpp
# RUN cd /tmp &&  cmake llama.cpp -B llama.cpp/build \
#     -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON -DLLAMA_CURL=ON
# RUN cd /tmp &&  cmake --build llama.cpp/build --config Release -j --clean-first --target llama-quantize llama-cli llama-gguf-split
# RUN cd /tmp && cp llama.cpp/build/bin/llama-* llama.cpp


# ENV PATH="${PATH}:/tmp/llama.cpp"

RUN curl https://github.com/ggerganov/llama.cpp/releases/download/b4681/llama-b4681-bin-ubuntu-x64.zip -L -o /tmp/llama-b4681-bin-ubuntu-x64.zip
RUN mkdir -p /tmp/llama-cpp && unzip /tmp/llama-b4681-bin-ubuntu-x64.zip -d /tmp/llama-cpp/
RUN ln -s /tmp/llama-cpp/build/bin/llama-gguf-split /opt/ml/code/llama-gguf-split
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/tmp/llama-cpp/build/bin"



ENTRYPOINT ["/bin/bash"]
