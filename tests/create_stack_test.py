import boto3
import json
import time
# 创建 CloudFormation 客户端
client = boto3.client('cloudformation')

# 定义堆栈名称
stack_name = 'emd-test-stack'

# 定义 CloudFormation 模板
template = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Resources": {
        "MyIAMRole": {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "RoleName": "DmaaModelPlaceholderRole",
                "AssumeRolePolicyDocument": json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "cloudformation.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                })
            }
        }
    }
}

# 创建堆栈
response = client.create_stack(
    StackName=stack_name,
    TemplateBody=json.dumps(template),
    Capabilities=['CAPABILITY_IAM','CAPABILITY_NAMED_IAM'] # 需要 IAM 权限
)

while True:
    # check stack exists
    try:
        stack_status = client.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
    except:
        stack_status = 'NOT_EXISTS'
    print("Stack status:", stack_status)
    if stack_status in ['CREATE_COMPLETE', 'ROLLBACK_COMPLETE',"UPDATE_COMPLETE"]:
        print(stack_status)
        break
    time.sleep(0.1)
