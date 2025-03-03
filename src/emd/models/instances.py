from . import Instance
from .utils.constants import InstanceType


g4dnxlarge_instance = Instance(
    instance_type=InstanceType.G4DNXLARGE,
    gpu_num=1,
    vcpu=4,
    memory=16,
    description="Amazon EC2 G4 instances are the industry’s most cost-effective and versatile GPU instances for deploying machine learning models such as image classification, object detection, and speech recognition, and for graphics-intensive applications such as remote graphics workstations, game streaming, and graphics rendering.",
    support_cn_region=True
)

g4dn2xlarge_instance = Instance(
    instance_type=InstanceType.G4DN2XLARGE,
    gpu_num=1,
    vcpu=8,
    memory=32,
    description="Amazon EC2 G4 instances are the industry’s most cost-effective and versatile GPU instances for deploying machine learning models such as image classification, object detection, and speech recognition, and for graphics-intensive applications such as remote graphics workstations, game streaming, and graphics rendering.",
    support_cn_region=True
)

g4dn4xlarge_instance = Instance(
    instance_type=InstanceType.G4DN4XLARGE,
    gpu_num=1,
    vcpu=16,
    memory=64,
    description="Amazon EC2 G4 instances are the industry’s most cost-effective and versatile GPU instances for deploying machine learning models such as image classification, object detection, and speech recognition, and for graphics-intensive applications such as remote graphics workstations, game streaming, and graphics rendering.",
    support_cn_region=True
)

g4dn8xlarge_instance = Instance(
    instance_type=InstanceType.G4DN8XLARGE,
    gpu_num=1,
    vcpu=32,
    memory=128,
    description="Amazon EC2 G4 instances are the industry’s most cost-effective and versatile GPU instances for deploying machine learning models such as image classification, object detection, and speech recognition, and for graphics-intensive applications such as remote graphics workstations, game streaming, and graphics rendering.",
    support_cn_region=True
)

g4dn16xlarge_instance = Instance(
    instance_type=InstanceType.G4DN16XLARGE,
    gpu_num=1,
    vcpu=64,
    memory=256,
    description="Amazon EC2 G4 instances are the industry’s most cost-effective and versatile GPU instances for deploying machine learning models such as image classification, object detection, and speech recognition, and for graphics-intensive applications such as remote graphics workstations, game streaming, and graphics rendering.",
    support_cn_region=True
)

g4dn12xlarge_instance = Instance(
    instance_type=InstanceType.G4DN12XLARGE,
    gpu_num=4,
    vcpu=48,
    memory=192,
    description="Amazon EC2 G4 instances are the industry’s most cost-effective and versatile GPU instances for deploying machine learning models such as image classification, object detection, and speech recognition, and for graphics-intensive applications such as remote graphics workstations, game streaming, and graphics rendering.",
    support_cn_region=True
)



g5dxlarge_instance = Instance(
    instance_type=InstanceType.G5dXLARGE,
    gpu_num=1,
    vcpu=4,
    memory=16,
    description="Amazon EC2 G5 instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton5 processors.",
    support_cn_region=True
)
g5d2xlarge_instance = Instance(
    instance_type=InstanceType.G5d2XLARGE,
    gpu_num=1,
    vcpu=8,
    memory=32,
    description="Amazon EC2 G5 instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton5 processors.",
    support_cn_region=True
)
g5d4xlarge_instance = Instance(
    instance_type=InstanceType.G5d4XLARGE,
    gpu_num=1,
    vcpu=16,
    memory=64,
    description="Amazon EC2 G5 instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton5 processors.",
    support_cn_region=True
)
g5d8xlarge_instance = Instance(
    instance_type=InstanceType.G5d8XLARGE,
    gpu_num=1,
    vcpu=32,
    memory=128,
    description="Amazon EC2 G5 instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton5 processors.",
    support_cn_region=True
)

g5d12xlarge_instance = Instance(
    instance_type=InstanceType.G5d12XLARGE,
    gpu_num=4,
    vcpu=48,
    memory=192,
    description="Amazon EC2 G5 instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton5 processors.",
    support_cn_region=True
)
g5d16xlarge_instance = Instance(
    instance_type=InstanceType.G5d16XLARGE,
    gpu_num=1,
    vcpu=64,
    memory=256,
    description="Amazon EC2 G5 instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton5 processors.",
    support_cn_region=True
)
g5d24xlarge_instance = Instance(
    instance_type=InstanceType.G5d24XLARGE,
    gpu_num=4,
    vcpu=96,
    memory=384,
    description="Amazon EC2 G5 instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton5 processors.",
    support_cn_region=True
)

g5d48xlarge_instance = Instance(
    gpu_num=8,
    vcpu=192,
    memory=768,
    instance_type=InstanceType.G5d48XLARGE,
    description="Amazon EC2 G5 instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton5 processors.",
    support_cn_region=True
)

g6exlarge_instance = Instance(
    instance_type=InstanceType.G6eXLARGE,
    gpu_num=1,
    vcpu=4,
    memory=32,
    description="Amazon EC2 G6e instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton6 processors.",
    support_cn_region=False
)


g6e2xlarge_instance = Instance(
    instance_type=InstanceType.G6e2XLARGE,
    gpu_num=1,
    vcpu=8,
    memory=64,
    description="Amazon EC2 G6e instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton6 processors.",
    support_cn_region=False
)

g6e4xlarge_instance = Instance(
    instance_type=InstanceType.G6e4XLARGE,
    gpu_num=1,
    vcpu=16,
    memory=128,
    description="Amazon EC2 G6e instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton6 processors.",
    support_cn_region=False
)

g6e8xlarge_instance = Instance(
    instance_type=InstanceType.G6e8XLARGE,
    gpu_num=1,
    vcpu=32,
    memory=256,
    description="Amazon EC2 G6e instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton6 processors.",
    support_cn_region=False
)

g6e16xlarge_instance = Instance(
    instance_type=InstanceType.G6e16XLARGE,
    gpu_num=1,
    vcpu=64,
    memory=512,
    description="Amazon EC2 G6e instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton6 processors.",
    support_cn_region=False
)
g6e12xlarge_instance = Instance(
    instance_type=InstanceType.G6e12XLARGE,
    gpu_num=4,
    vcpu=48,
    memory=384,
    description="Amazon EC2 G6e instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton6 processors.",
    support_cn_region=False
)

g6e24xlarge_instance = Instance(
    instance_type=InstanceType.G6e24XLARGE,
    gpu_num=4,
    vcpu=96,
    memory=768,
    description="Amazon EC2 G6e instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton6 processors.",
    support_cn_region=False
)

g6e48xlarge_instance = Instance(
    instance_type=InstanceType.G6e48XLARGE,
    gpu_num=8,
    vcpu=192,
    memory=1536,
    description="Amazon EC2 G6e instances are powered by the latest generation of Amazon GPU-optimized processors, the AWS Graviton6 processors.",
    support_cn_region=False
)


inf2dxlarge_instance = Instance(
    instance_type=InstanceType.INF2DXLARGE,
    neuron_core_num=2,
    vcpu=4,
    memory=16,
    description="Amazon Inferentia2 chips.",
    support_cn_region=False
)

inf2d8xlarge_instance = Instance(
    instance_type=InstanceType.INF2D8XLARGE,
    neuron_core_num=2,
    vcpu=32,
    memory=128,
    description="Amazon Inferentia2 chips.",
    support_cn_region=False
)

inf2d24xlarge_instance = Instance(
    instance_type=InstanceType.INF2D24XLARGE,
    neuron_core_num=12,
    vcpu=96,
    memory=384,
    description="Amazon Inferentia2 chips.",
    support_cn_region=False
)

inf2d48xlarge_instance = Instance(
    instance_type=InstanceType.INF2D48XLARGE,
    neuron_core_num=24,
    vcpu=192,
    memory=768,
    description="Amazon Inferentia2 chips.",
    support_cn_region=False
)

local_instance = Instance(
    instance_type=InstanceType.LOCAL,
    gpu_num=None,
    vcpu=0,
    memory=0,
    description="local instance",
    support_cn_region=True
)
