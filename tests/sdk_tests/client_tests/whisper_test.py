import os
import sys
# sys.path.append("src/pipeline")
from emd.sdk.clients.sagemaker_client import SageMakerClient

pyload = dict(
    audio_input = "s3://llm-bot-dev-uiconstructuicloudfrontloggingbuckete6-kekcadtyn2hd/vad_example.wav",
    model="large-v3-turbo",
    # bucket = "llm-bot-dev-uiconstructuicloudfrontloggingbuckete6-kekcadtyn2hd",
    # key="vad_example.json",
    config={}
)

client = SageMakerClient(

    # region='us-west-2',
    # endpoint_name="whisper-huggingface-2024-11-29-04-32-00"
)
print(client.invoke(pyload))
