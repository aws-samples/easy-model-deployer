<!-- to preview the time sequence diagram, use mermaid or install mermaid extension in vscode -->
<!-- to export, install mermaid cli: yarn global add @mermaid-js/mermaid-cli
mmdc -s 2 -i <file path> -e png -->
# Time sequence diagram of invoke a deployed model for the first time
```mermaid
sequenceDiagram
    autonumber
    actor User
    User->>+WebUI: Invoke model for Text2SQL_config(Text2SQL+Qwen2.5-72B-instruct+vllm+Sagemaker-g5.12x.large)
        box rgb(243, 255, 242) DMAA App Layer
        participant Application API
    end

    box rgb(250, 233, 232) DMAA Core Layer
    participant Core API
    participant DB
    participant Sagemaker
    end

    WebUI->>+Application API: Call dmaa.app.invoke(Text2SQL_config, param)
    Application API->>Core API: Call dmaa.core.retrieve_db_deploy(Text2SQL_config)
    Core API->>DB: retrieve db
    DB-->>Core API: The deploy task is finished
    Core API-->>Application API: The deploy task is finished
    Application API->>Core API: Call dmaa.core.invoke() with parameters
    Core API->>Sagemaker: Call sagemaker endpoint 
    Sagemaker-->>Core API: Return inference results
    Core API-->>Application API: Return inference results
    Application API-->>WebUI: Return inference results
    WebUI-->>User: display inference results of Text2SQL_config
```