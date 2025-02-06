from threading import Thread
from dmaa.sdk.clients.sagemaker_client import SageMakerClient
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

client = SageMakerClient(
    # model_id="Qwen2.5-72B-Instruct-AWQ"
    model_id="Qwen2.5-0.5B-Instruct"
)


def task():
    t0 = time.time()
    ret = client.invoke(pyload)
    print('elasped time: ',time.time()-t0)
    # print(ret)

if __name__ == "__main__":
    threads = []
    t0 = time.time()

    for i in range(40):
        time.sleep(0.01)
        t = Thread(target=task)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print("done, all task elapsed time: ",time.time()-t0)







