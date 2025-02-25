
# Invocation guidelines

## Use EMD to invoke model

```bash
emd invoke MODEL_ID MODEL_TAG (Optional)
```

### For LLM models
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

### For VLM models
1. upload image to a s3 path
![alt text](../images/sample.png)
```bash
aws s3 cp image.jpg s3://your-bucket/image.jpg
```

2. invoke the model
```bash
emd invoke  Qwen2-VL-7B-Instruct
...
Invoking model DeepSeek-R1-Distill-Qwen-7B with tag dev
...
```

### For Embedding models
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

### For Embedding models
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

### F


Deploy models to the cloud with EMD will use the following components in Amazon Web Services:

## Use the langchain interface to invoke model

## Use the
