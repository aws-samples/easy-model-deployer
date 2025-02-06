import sys
import time
import requests

class EC2Client:
    def __init__(self, host, model, stream):
        self.stream = stream
        self.host = host
        self.model = model

    def invoke(self, request):
        request["model"] = self.model
        response = requests.post(f"http://{self.host}:9000/invocations", json=request)
        if self.stream:
            for chunk in response.iter_content(chunk_size=3):
                sys.stdout.flush()
                time.sleep(0.1)
                sys.stdout.write(chunk.decode())
            sys.stdout.write("\n")
        else:
            print(response.json())