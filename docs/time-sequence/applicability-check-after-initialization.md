<!-- to preview the time sequence diagram, use mermaid or install mermaid extension in vscode -->
<!-- to export, install mermaid cli: yarn global add @mermaid-js/mermaid-cli
mmdc -s 2 -i <file path> -e png -->
# Time sequence diagram of applicability-check after DB initialization
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
    DB-->>Core API: Results of supported information relating to Text2SQL
    Core API-->>Application API: results from DB
    Application API-->>WebUI: applicability check results
    WebUI-->>User: display applicability check results: supported models/frameworks/infras/versions for Text2SQL
```