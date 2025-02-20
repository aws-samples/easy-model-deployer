from fastapi import FastAPI, Request
import uvicorn
import boto3
import json
import time

app = FastAPI()

# Initialize SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name='us-east-1')

# Define the SageMaker endpoint name
SAGEMAKER_ENDPOINT_NAME = 'EMD-QwenQwen2-beta-7B-Chat-ed3pqh-endpoint'

@app.post("/v1/chat/completions")
async def chat(request: Request):
    # Get the request payload
    payload = await request.json()
    model = payload.get("model", None)

    # Invoke the SageMaker endpoint
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT_NAME,
        ContentType='application/json',
        Body=json.dumps(payload)
    )

    # Parse the response from SageMaker
    response_body = json.loads(response['Body'].read().decode())
    print(response_body)

    # Transform the response to OpenAI-compatible format
    openai_response = {
        "id": "cmpl-12345",
        "object": "text_completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "text": choice,
                "index": idx,
                "logprobs": None,
                "finish_reason": "length"
            }
            for idx, choice in enumerate([response_body])
        ]
    }
    openai_response = response_body

    return openai_response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
