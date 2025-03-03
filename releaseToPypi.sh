#!/bin/bash

# Exit on any error
set -e

# Function to increment minor version
increment_version() {
    local version=$1
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)
    local patch=$(echo $version | cut -d. -f3)
    
    # Increment minor version
    patch=$((patch + 1))
    echo "${major}.${minor}.${patch}"
}

# Check if PYPI_TOKEN environment variable exists
if [ -z "$PYPI_TOKEN" ]; then
    echo "Error: PYPI_TOKEN environment variable is not set"
    echo "Please set it first:"
    echo "export PYPI_TOKEN=your_token_here"
    exit 1
fi

# Get current version from pyproject.toml
current_version=$(grep "^version = " pyproject.toml | cut -d'"' -f2)
echo "Current version: $current_version"

# Calculate new version
new_version=$(increment_version $current_version)
echo "New version: $new_version"

# Update version in pyproject.toml
sed -i.bak "s/^version = \"${current_version}\"/version = \"${new_version}\"/" pyproject.toml
rm pyproject.toml.bak

# Clean up old builds
echo "Cleaning up old builds..."
rm -rf dist/ build/ *.egg-info/

# Configure Poetry with PyPI token
echo "Configuring Poetry with PyPI token..."
poetry config pypi-token.pypi "${PYPI_TOKEN}"

# Build the package
echo "Building package..."
poetry build

# List built files
echo "Built files:"
ls -l dist/

# Publish to PyPI
echo "Publishing to PyPI..."
poetry publish

echo "Successfully published version ${new_version} to PyPI!"

# Waitting 30 seconds for verification
echo "Verifying installation..."
sleep 30
pip install --no-cache-dir easy-model-deployer==${new_version}

echo "Done! Try running: emd --help"
echo "Note to push the latest version in pyproject.toml as ${new_version}, please update it manually."
