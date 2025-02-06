<!-- to preview the time sequence diagram, use mermaid or install mermaid extension in vscode -->
<!-- to export, install mermaid cli: yarn global add @mermaid-js/mermaid-cli
mmdc -s 2 -i <file path> -e png -->
# Time sequence diagram of deploy a model in rolling mode
```mermaid
sequenceDiagram
    autonumber
    actor User
    User->>+WebUI: Deploy model for Text2SQL_config(Text2SQL+Qwen2.5-72B-instruct+vllm+Sagemaker-g5.12x.large)
        box rgb(243, 255, 242) DMAA App Layer
        participant Application API
    end

    box rgb(250, 233, 232) DMAA Core Layer
    participant Core API
    participant Batch
    participant DB
    participant Sagemaker
    end

    WebUI->>+Application API: Call dmaa.app.deploy(Text2SQL_config, rolling=True)
    Application API->>Core API: Call dmaa.core.retrieve_db_deploy(Text2SQL_config)
    Core API->>DB: Check the status of model/image/deploy task
    DB-->>Core API: Db resulsts of related task
    Core API-->>Application API: Model and image task id
    loop ModelTaskCheck
        Application API->>Core API: Call dmaa.core.batch_job_check(Text2SQL_config, model)
        Core API->>Batch: Model task check
        Batch-->>Core API: Batch job status
        Core API-->>Application API: Model task on-going
        Application API->>Core API: Call dmaa.core.batch_job_check(Text2SQL_config, image)
        Core API->>Batch: Image task check
        Batch-->>Core API: Batch job status
        Core API-->>Application API: Image task on-going
    end
    Application API->>Core API: Call dmaa.core.update_db() for model/image task
    Core API->>DB: Update model/image to finished
    DB-->>Core API: Update results
    Core API-->>Application API: Update results
    Application API->>Core API: Call dmaa.core.sagemaker_deploy() to deploy model
    Core API->>Sagemaker: Initilize Amazon sagemaker endpoint deployment
    Sagemaker-->>Core API: Amazon sagemaker deployment task id
    Core API-->>Application API: Launch the deployment task
    loop DeployTaskCheck
        Application API->>Core API: Call dmaa.core.sagemaker_job_check(Text2SQL_config)
        Core API->>Sagemaker: deployment task check
        Sagemaker-->>Core API: deployment task on-going
        Core API-->>Application API: deployment task on-going
    end
    Application API->>Core API: Call dmaa.core.update_db()
    Core API->>DB: Update the status of model/image/deploy task
    DB-->>Core API: Task results
    Core API-->>Application API: Update model/image/deploy task status
    Application API-->>WebUI: deploy status of Text2SQL_config: model(finished), image(finished), deploy(finished)
    WebUI-->>User: display deploy status of Text2SQL_config
```