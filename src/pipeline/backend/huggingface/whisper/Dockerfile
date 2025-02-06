FROM 763104351884.dkr.ecr.{{REGION}}.amazonaws.com/pytorch-inference:2.3.0-gpu-py311-cu121-ubuntu20.04-ec2

# 设置环境变量
ENV PATH="/opt/ml/code:$PATH"

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    jq \
    zip \
    htop \
    screen \
    libgl1-mesa-glx \
    wget \
    ca-certificates \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*


# 刷新动态链接库缓存
RUN ldconfig -v

# 复制 requirements.txt 并安装 Python 依赖项
COPY ./backend/huggingface/whisper/requirements.txt /opt/ml/code/
COPY ./backend/huggingface/whisper/download_model.py /opt/ml/code/

RUN pip install --no-cache-dir -r /opt/ml/code/requirements.txt

# 安装额外的 Python 包 --no-cache-dir
RUN pip install --no-cache-dir fastapi uvicorn openai-whisper huggingface-hub

COPY ./ /opt/ml/code/
RUN cd /opt/ml/code && python download_model.py


# Set environment variables
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/ml/code:$PATH"

# 复制应用程序代码
WORKDIR /opt/ml/code
RUN mkdir /opt/ml/code/tmp

# 确认 ffmpeg 安装
RUN ffmpeg -version

ENTRYPOINT ["python3", "fastapi_serve.py"]
