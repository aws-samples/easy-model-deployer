
# Architecture
Deploy models to the cloud with EMD will use the following components in Amazon Web Services:

![alt text](emd-architecture.png)

1. User/Client initiates model deployment task, triggering pipeline to start model building.

2. AWS CodeBuild constructs the large model using predefined configuration and publishes it to Amazon ECR.

3. AWS CloudFormation creates a model infrastructure stack based on user selection and deploys the model from ECR to AWS services (Amazon SageMaker, EC2, ECS).
