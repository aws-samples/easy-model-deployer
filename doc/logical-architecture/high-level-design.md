<!-- to preview the time sequence diagram, use mermaid or install mermaid extension in vscode -->
<!-- to export, install mermaid cli: yarn global add @mermaid-js/mermaid-cli
mmdc -s 2 -i <file path> -e png -->
# Time sequence diagram of applicability-check after DB initialization
```mermaid
block-beta
    block:group1:3
        columns 3
        B["2 Deploy Model Anywhere on AWS (DMAA) Application Layer"]:3
        %% columns auto (default)
        B1["Translation"] B2["Text to SQL"] B3["Image Understanding"] B4["Summarization"] B5["Embedding"]
    end
```