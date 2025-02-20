<!-- to preview the time sequence diagram, use mermaid or install mermaid extension in vscode -->
<!-- to export, install mermaid cli: yarn global add @mermaid-js/mermaid-cli
mmdc -s 2 -i <file path> -e png -->
# Time sequence diagram of deploy a model for the first time check
```mermaid
sequenceDiagram
    autonumber
    actor User
    User->>+WebUI: Deploy model for Text2SQL_config(Text2SQL+Qwen2.5-72B-instruct+vllm+Sagemaker-g5.12x.large)
        box rgb(243, 255, 242) EMD App Layer
        participant Application API
    end

    box rgb(250, 233, 232) EMD Core Layer
    participant Core API
    participant DB
    participant Batch
    end

    WebUI->>+Application API: Call emd.app.deploy(Text2SQL_config)
    Application API->>Core API: Call emd.core.retrieve_db_deploy(Text2SQL_config)
    Core API->>DB: Check the status of model/image/deploy task
    DB-->>Core API: Task results
    Core API-->>Application API: No available model/image/deploy task status
    Application API->>Core API: Call emd.core.model_prepare(Text2SQL_config)
    Core API->>Batch: Initilize batch job for preparing model file
    Batch-->>Core API: Batch job launched
    Core API-->>Application API: Batch job launched
    Application API->>Core API: Call emd.core.image_build(Text2SQL_config)
    Core API->>Batch: Initilize batch job for building images
    Batch-->>Core API: Batch job launched
    Core API-->>Application API: Batch job launched
    Application API->>Core API: Call emd.core.update_db()
    Core API->>DB: Update the status of model/image/deploy task
    DB-->>Core API: Task results
    Core API-->>Application API: Update model/image/deploy task status
    Application API-->>WebUI: deploy status of Text2SQL_config: model(initial), image(initial), deploy(N/A)
    WebUI-->>User: display deploy status of Text2SQL_config
```
