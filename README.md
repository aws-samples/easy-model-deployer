## Installation Guide

### Prerequisites

Ensure you have Python 3 installed on your system. If not, download and install it from the [official Python website](https://www.python.org/downloads/).

### Installing pip

If `pip` is not installed, follow one of the methods below:

#### Method 1: Using ensurepip

Run the following command to install or upgrade `pip`:

```bash
python3 -m ensurepip --upgrade
```

#### Method 2: Using get-pip.py

Download the `get-pip.py` script and execute it:

```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

### Installing DMAA

To install the DMAA package, execute the following steps:

1. **(Optional)** Create and activate a virtual environment:

    Creating a virtual environment is recommended if you want to isolate the package and its dependencies from other Python projects on your system. This helps prevent version conflicts and keeps your global Python environment clean.

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2. **Install the package**:

    ```bash
    pip install ./
    ```

This command installs the package along with its dependencies.


3. **(Optional) Install the package with LangChain client**:
    ```bash
    pip install .[langchain_client]
    ```


## Usage Instructions

After successful installation, use the following command to access the CLI help:

```bash
dmaa --help
```

This command displays the available options and commands for the DMAA CLI.
