#!/bin/bash

COMMIT_HASH=$(git rev-parse --short=8 HEAD)
sed -i "s/^COMMIT_HASH = .*/COMMIT_HASH = \"$COMMIT_HASH\"/" src/emd/revision.py
# update supported models
python tests/generate_supported_models_doc_cli.py -o docs/en/supported_models.md
poetry build
