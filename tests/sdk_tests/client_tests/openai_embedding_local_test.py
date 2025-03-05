# SPDX-License-Identifier: Apache-2.0

from openai import OpenAI
from  threading import Thread
import time
# Modify OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"


def run():
    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=openai_api_key,
        base_url=openai_api_base,
    )

    models = client.models.list()
    model = models.data[0].id
    t0 = time.time()
    responses = client.embeddings.create(
        # input=[
        #     "Hello my name is",
        #     "The best thing about vLLM is that it supports many different models"
        # ],
        input=[
         'The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.'
        ],
        model=model,
    )
    print(f'elapsed time: {time.time()-t0}')

    # for data in responses.data:
    #     print(data.embedding)  # list of float of len 4096


if __name__ == "__main__":
    threads = []
    t0 = time.time()

    for i in range(2000):
        # time.sleep(0.01)
        # t = Thread(target=task)
        t = Thread(target=run)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print("done, all task elapsed time: ",time.time()-t0)
