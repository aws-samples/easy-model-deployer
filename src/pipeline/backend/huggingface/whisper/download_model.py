import whisper
from huggingface_hub import snapshot_download

model = whisper.load_model("large-v3", download_root="./models/", in_memory=True)
model = whisper.load_model("large-v3-turbo", download_root="./models/", in_memory=True)

vad_dir = snapshot_download("funasr/fsmn-vad", local_dir="./models/vad_model")
