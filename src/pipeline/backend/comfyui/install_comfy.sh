#!/bin/bash

echo "---------------------------------------------------------------------------------"
echo "install comfy..."

export INITIAL_COMFY_COMMIT_ROOT=f7695b5f9e007136da72bd3e79d601e2814a3890
export LTXV_COMMIT_ID=4c5add5f4693e5bf55b58aad99326fab9e9b4a53

rm -rf ComfyUI

git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI || exit 1
git reset --hard ${INITIAL_COMFY_COMMIT_ROOT}
cd ../

echo "---------------------------------------------------------------------------------"
echo "build comfy..."

cd ComfyUI || exit 1

git clone https://github.com/ltdrdata/ComfyUI-Manager.git custom_nodes/ComfyUI-Manager

git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git custom_nodes/ComfyUI-VideoHelperSuite
git clone https://github.com/Lightricks/ComfyUI-LTXVideo.git custom_nodes/ComfyUI-LTXVideo
cd custom_nodes/ComfyUI-LTXVideo || exit 1
git reset --hard "$LTXV_COMMIT_ID"
cd ../../

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install boto3
pip install aws_xray_sdk
pip install fastapi
pip install uvicorn
pip install watchdog
pip install python-dotenv
pip install httpx
pip install onnxruntime
pip install diffusers
pip install sentencepiece
pip install insightface==0.7.3
pip install opencv-python

pip install -r custom_nodes/ComfyUI-Manager/requirements.txt
pip install -r custom_nodes/ComfyUI-VideoHelperSuite/requirements.txt
#pip install -r custom_nodes/ComfyUI-LTXVideo/requirements.txt
pip install av>=10.0.0
pip install ltx-video@git+https://github.com/Lightricks/LTX-Video@ltx-video-0.9.1

pip install https://github.com/openai/CLIP/archive/d50d76daa670286dd6cacf3bcd80b5e4823fc8e1.zip
pip install https://github.com/mlfoundations/open_clip/archive/bb6e834e9c70d9c27d0dc3ecedeebeaeb1ffad6b.zip
pip install protobuf==3.20.2
pip install open-clip-torch==2.20.0
pip install xformers
pip install torchaudio
pip install transformers -U
pip install accelerate
pip install omegaconf
