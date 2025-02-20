from threading import Thread
from emd.sdk.clients.sagemaker_client import SageMakerClient
import time

pyload = {
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": "9.11和9.9哪个更大？"}]

            }
        ],
        "max_tokens": 512,
        "temperature": 1.0,
        "stream":False
    }




def task():
    client = SageMakerClient(
    # model_id="Qwen2.5-72B-Instruct-AWQ"
    # model_id="Qwen2.5-0.5B-Instruct"
    model_id="Qwen2.5-72B-Instruct-AWQ"
)
    t0 = time.time()

    ret = client.invoke(pyload)
    print('elasped time: ',time.time()-t0)
    # print(ret)


def task_local_deploy():
    t0 = time.time()
    from openai import OpenAI
    client = OpenAI(base_url="http://127.0.0.1:8080/v1",api_key="sg")
    client.chat.completions.create(
        model="Qwen2.5-7B-Instruct",
        **pyload
    )
    print('elasped time: ', time.time()-t0)

if __name__ == "__main__":
    threads = []
    t0 = time.time()

    for i in range(10):
        # time.sleep(0.01)
        # t = Thread(target=task)
        t = Thread(target=task_local_deploy)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print("done, all task elapsed time: ",time.time()-t0)
