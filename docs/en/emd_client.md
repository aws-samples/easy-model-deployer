
# Usse EMD client to invoke deployed models

```bash
emd invoke MODEL_ID MODEL_TAG (Optional)
```

## LLM models
```bash
emd invoke  DeepSeek-R1-Distill-Qwen-7B
...
Invoking model DeepSeek-R1-Distill-Qwen-7B with tag dev
Write a prompt, press Enter to generate a response (Ctrl+C to abort),
User: how to solve the problem of making more profit
Assistant:<think>

Okay, so I need to figure out how to make more profit. Profit is basically the money left after subtracting costs from revenue, right? So, increasing profit means either making more money from sales or reducing the
expenses. Let me think about how I can approach this.
...
```

## VLM models
1. upload image to a s3 path
![alt text](../images/sample.png)
```bash
aws s3 cp image.jpg s3://your-bucket/image.jpg
```

2. invoke the model
```bash
emd invoke  Qwen2-VL-7B-Instruct
...
Invoking model Qwen2-VL-7B-Instruct with tag dev
Enter image path(local or s3 file): s3://your-bucket/image.jpg
Enter prompt: What's in this image?
...
```

### Video(Txt2edding) models
1. input prompt for video generation
```bash
emd invoke txt2video-LTX
...
Invoking model txt2video-LTX with tag dev
Write a prompt, press Enter to generate a response (Ctrl+C to abort),
User: Two police officers in dark blue uniforms and matching hats enter a dimly lit room through a doorway on the left side of the frame. The first officer, with short brown hair and a mustache, steps inside first, followed by his partner, who has a shaved head and a goatee. Both officers have serious expressions and maintain a steady pace as they move deeper into the room. The camera remains stationary, capturing them from a slightly low angle as they enter. The room has exposed brick walls and a corrugated metal ceiling, with a barred window visible in the background. The lighting is low-key, casting shadows on the officers' faces and emphasizing the grim atmosphere. The scene appears to be from a film or television show.
...
```
2. download generated video from **output_path**

##  Embedding models
```bash
emd invoke bge-base-en-v1.5
...
Invoking model bge-base-en-v1.5 with tag dev
Enter the sentence: hello
...
```

##  Rerank models
```bash
emd invoke bge-reranker-v2-m3
...
Enter the text_a (string): What is the capital of France?
Enter the text_b (string): The capital of France is Paris.
...
```
