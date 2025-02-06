#!/usr/bin/env bash

# This is required to activate conda environment
eval "$(conda shell.bash hook)"

CONDA_ENV=${1:-""}
if [ -n "$CONDA_ENV" ]; then
    conda create -n $CONDA_ENV python=3.10 -y
    conda activate $CONDA_ENV
else
    echo "Skipping conda environment creation. Make sure you have the correct environment activated."
fi

# This is required to enable PEP 660 support
pip install --upgrade pip

# Install DMAA
pip install -e .