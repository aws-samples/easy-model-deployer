<!-- to preview the time sequence diagram, use mermaid or install mermaid extension in vscode -->
<!-- to export, install mermaid cli: yarn global add @mermaid-js/mermaid-cli
mmdc -s 2 -i <file path> -e png -->
# Time sequence diagram of applicability-check for the first time check
```mermaid
sequenceDiagram
    autonumber
    actor User
    User->>+WebUI: List supported models for an application, e.g. Text2SQL
    box rgb(243, 255, 242) DMAA App Layer
    participant Application API
    end

    box rgb(250, 233, 232) DMAA Core Layer
    participant Core API
    participant DB
    end

    WebUI->>+Application API: Call dmaa.app.list_app('Text2SQL')
    Application API->>Core API: Call dmaa.core.retrieve_db('Text2SQL')
    Core API->>DB: Retrive relating db
    DB-->>Core API: Db check results
    Core API-->>Application API: Fail to find valid db
    Application API->>Core API: Call dmaa.core.initialize_db('Text2SQL')
    Core API->>DB: Initialize db based on DMAA configuration file
    DB-->>Core API: Initilization results
    Core API-->>Application API: Finish initilization
    Application API-->>WebUI: applicability check results from DMAA configuration file
    WebUI-->>User: display applicability check results: supported models/frameworks/infras/versions for Text2SQL
```