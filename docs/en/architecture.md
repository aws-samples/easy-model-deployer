# Architecture

EMD deploys models to AWS using a simple three-step process:

![EMD Architecture Diagram](emd-architecture.png)

1. User/Client initiates model deployment task, triggering pipeline to start model building.

2. AWS CodeBuild constructs the large model using predefined configuration and publishes it to Amazon ECR.

3. AWS CloudFormation creates a model infrastructure stack based on user selection and deploys the model from ECR to AWS services (Amazon SageMaker, EC2, ECS).

## Key AWS Services Used

- **CodePipeline**: Orchestrates the entire workflow
- **CodeBuild**: Builds model containers
- **CloudFormation**: Provisions infrastructure
- **ECR**: Stores model containers
- **Target Services**: SageMaker, EC2, or ECS hosts your model

EMD handles all IAM permissions and security configurations automatically.

## Cost Considerations

EMD uses pay-as-you-go AWS services with costs varying based on your deployment choices:

### Compute Resources (Primary Cost)

| Service | Instance Type | Approx. Cost (US East) | Notes |
|---------|---------------|------------------------|-------|
| EC2 (Default) | g5.xlarge (1 GPU) | $1.006/hour | 4 vCPU, 16GB RAM, 1 NVIDIA A10G GPU |
| EC2 | g5.2xlarge (1 GPU) | $1.212/hour | 8 vCPU, 32GB RAM, 1 NVIDIA A10G GPU |
| EC2 | g5.4xlarge (1 GPU) | $1.624/hour | 16 vCPU, 64GB RAM, 1 NVIDIA A10G GPU |
| SageMaker | ml.g5.xlarge | ~$1.307/hour | ~30% premium over EC2 pricing |
| SageMaker | ml.g5.2xlarge | ~$1.575/hour | ~30% premium over EC2 pricing |

* Costs increase with:
  * Larger models requiring more memory
  * Higher throughput requirements needing more vCPUs
  * Longer running deployments (24/7 vs. on-demand)

### Storage Costs

| Service | Component | Approx. Cost | Notes |
|---------|-----------|--------------|-------|
| ECR | Container Storage | $0.10/GB-month | Model containers can range from 5GB to 50GB+ |
| S3 | Model Artifacts | $0.023/GB-month | Large models can be several GB each |
| EBS | EC2 Instance Storage | $0.10/GB-month | Default 150GB gp2 volume for EC2 instances |

### Networking Costs

| Component | Approx. Cost | Notes |
|-----------|--------------|-------|
| Load Balancer | $0.0225/hour + $0.008/GB | Required for API access |
| Data Transfer Out | $0.09/GB | Costs for responses from model API |
| VPC Endpoints | $0.01/hour | Optional for enhanced security |

### Pipeline Execution Costs

| Service | Component | Approx. Cost | Notes |
|---------|-----------|--------------|-------|
| CodeBuild | BUILD_GENERAL1_LARGE | $0.10/minute | Used during model building phase |
| CodePipeline | Pipeline Execution | $1.00/pipeline/month | Plus $0.01 per pipeline execution |

### Cost Optimization Strategies

1. **Right-size your instances**:
   * Match instance type to your model's memory and compute requirements
   * Consider CPU-only instances for smaller models

2. **Use auto-scaling**:
   * Set appropriate min/max capacity values
   * Configure scale-in periods during low usage times

3. **Implement lifecycle policies**:
   * Clean up unused ECR images
   * Remove old model artifacts from S3

4. **Consider Spot instances**:
   * Use EC2 Spot instances for non-critical workloads
   * Can reduce costs by up to 70% compared to On-Demand pricing

5. **Monitor and analyze costs**:
   * Use AWS Cost Explorer to identify cost drivers
   * Set up AWS Budgets to alert on unexpected spending

## Security Considerations

### API Key Authentication

EMD supports API key authentication for securing access to your deployed models:

#### Setting Up API Keys

**Using Command Line:**
```bash
emd deploy --model-id <model-id> --instance-type <instance-type> --engine-type <engine-type> --service-type <service-type> --extra-params '{
  "service_params": {
    "api_key": "your-secure-api-key"
  }
}'
```

**Using Interactive CLI:**
When prompted for "Extra Parameters" during `emd deploy`, enter:
```json
{
  "service_params": {
    "api_key": "your-secure-api-key"
  }
}
```

#### Managing API Keys

- **Storage**: Keys are securely stored in AWS Secrets Manager
- **Access**: Keys can be retrieved from the AWS Secrets Manager console
- **Rotation**: Update keys periodically through Secrets Manager or by redeploying

#### Using API Keys

Include the API key in your requests to the model endpoint:
```bash
curl -X POST https://your-endpoint.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "your-model-id/tag",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

With Python:
```python
import openai

client = openai.OpenAI(
    base_url="https://your-endpoint.com",
    api_key="YOUR_API_KEY"
)

response = client.chat.completions.create(
    model="your-model-id/tag",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Security Best Practices

1. **Enable HTTPS**:
   ```
   # Create certificate in AWS Certificate Manager
   aws acm request-certificate --domain-name your-model-endpoint.com

   # Update ALB listener to use HTTPS
   aws elbv2 create-listener --load-balancer-arn <your-alb-arn> \
     --protocol HTTPS --port 443 \
     --certificates CertificateArn=<certificate-arn> \
     --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06 \
     --default-actions Type=forward,TargetGroupArn=<target-group-arn>
   ```

2. **Rotate API keys regularly**:
   * Update keys in AWS Secrets Manager
   * Redeploy models with new keys or update existing keys

3. **Implement network isolation** when needed:
   * Deploy in private subnets with NAT gateway
   * Use VPC endpoints for AWS services
