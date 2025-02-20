from typing import Iterable, List
import sys
import time

from backend.backend import BackendBase
sys.path.append("/opt/")
import whisper
import multiprocessing as mp
from funasr import AutoModel as FunasrModel
from silero_vad import get_speech_timestamps, load_silero_vad, read_audio

import boto3
import botocore
import json
import os
from emd.models.utils.logger_utils import get_logger
from concurrent.futures import ProcessPoolExecutor,as_completed

logger = get_logger(__name__)

client_config = botocore.config.Config(
            max_pool_connections=50, connect_timeout=3600, read_timeout=3600
        )
s3_client = boto3.client("s3", config=client_config)

ctx = mp.get_context("spawn")

def is_significant_overlap(a_start, a_end, b_start, b_end, min_overlap=0.1):
    overlap_duration = min(a_end, b_end) - max(a_start, b_start)
    return overlap_duration / (a_end - a_start) > min_overlap


# Updated function to check for overlaps considering minimum overlap of 0.5 seconds
def find_overlaps_with_threshold(list_a, list_b, min_overlap=0.1):
    i, j = 0, 0
    matches = []

    while i < len(list_a) and j < len(list_b):
        cur_a = list_a[i]
        a_start, a_end, _ = cur_a["start"], cur_a["end"], cur_a["text"]
        b_start, b_end = list_b[j]["start"], list_b[j]["end"]

        if a_end < b_start:
            i += 1
        elif b_end < a_start:
            j += 1
        else:
            if is_significant_overlap(a_start, a_end, b_start, b_end, min_overlap):
                if not matches or matches[-1] != cur_a:
                    matches.append(cur_a)
            if a_end < b_end:
                i += 1
            else:
                j += 1

    return matches


def inference(source, model_type, **decode_options):
    logger.info(f"source:{source}")
    logger.info(f"decode_options:{decode_options}")

    # decode_options = {
    #               "language":language,
    #               "temperature":0.1,
    #               # "sample_len":30,
    #               "best_of":5,
    #               "beam_size":5,
    #               "patience":3.0,
    #               "word_timestamps":True,
    #               "no_speech_threshold":0.6,
    #               "logprob_threshold":None,
    #               "compression_ratio_threshold":2.4,
    #               "condition_on_previous_text":False,
    #              }

    model = whisper.load_model(
        model_type, download_root="/opt/ml/code/models/", in_memory=True, device="cuda"
    )
    result = model.transcribe(source, **decode_options)

    # language detection
    audio = whisper.load_audio(source)
    mel = whisper.log_mel_spectrogram(
        audio, model.dims.n_mels, padding=whisper.audio.N_SAMPLES
    ).to(model.device)
    mel_segment = whisper.pad_or_trim(mel, whisper.audio.N_FRAMES)
    _, probs = model.detect_language(mel_segment)
    lang = max(probs, key=probs.get)

    if lang == "zh":
        vad_model = FunasrModel(
            model="/opt/ml/code/models/vad_model", model_revision="v2.0.4"
        )
        res = vad_model.generate(input=source)
        speech_timestamps = []
        for row in res[0]["value"]:
            speech_timestamps.append({"start": row[0] / 1000, "end": row[1] / 1000})
    else:
        vad_model = load_silero_vad()
        wav = read_audio(source)
        speech_timestamps = get_speech_timestamps(
            wav,
            vad_model,
            return_seconds=True,
            threshold=0.2,  # Return speech timestamps in seconds (default is samples)
        )
    segments = find_overlaps_with_threshold(result["segments"], speech_timestamps)
    for index, item in enumerate(segments):
        item["id"] = index
    result["segments"] = segments
    logger.info("<<<<result:",result)
    os.remove(source)
    return result

class WhisperBackend(BackendBase):
    def __init__(self,*args,**kwargs):
        super().__init__(
              *args,
              **kwargs
        )
        self.s3_client = None

    def start(self):
        client_config = botocore.config.Config(
            max_pool_connections=50, connect_timeout=3600, read_timeout=3600
        )
        self.s3_client = boto3.client("s3", config=client_config)
        return

    def invoke(self, request:dict):
        data = request
        s3_url = data["audio_input"]
        model_type = data["model"]
        output_bucket = data["bucket"]
        output_key = data["key"]
        decode_options = data["config"]
        file_name = s3_url.split("/")[-1]
        download_file_name = "/opt/ml/code/tmp/" + file_name
        logger.info(f"request body: {data}")

        bucket = s3_url.replace("s3://", "").split("/")[0]
        file_prefix = s3_url.replace(f"s3://{bucket}/", "")

        logger.info(f"<<<<download video file: {download_file_name}")
        try:
            s3_client.download_file(bucket, file_prefix, download_file_name)
        except Exception as e:
            logger.error("<<<<download error:", e)
            return {'status': 'bad response'}

        print("download success")
        # my_process = ctx.Process(
        #     target=inference,
        #     args=(download_file_name, output_bucket, output_key, model_type),
        #     kwargs=decode_options,
        # )
        # my_process.start()
        logger.info(">>>>>>>>>processing!!!")
        result = inference(download_file_name, model_type, **decode_options)
        # time.sleep(10)
        # return {'status': 'processing'}
        return result

    def load_model(self, model_type:str):
        return
