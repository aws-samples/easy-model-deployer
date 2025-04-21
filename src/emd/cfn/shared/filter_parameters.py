import json
import sys
import re
from pathlib import Path

def read_template_parameters(template_path):
    """Read CloudFormation template and extract parameter names"""
    with open(template_path) as f:
        content = f.read()

    # Find Parameters section (match until next section or end of file)
    params_section = re.search(
        r'^Parameters:\s*$(.*?)(?=^\w|\Z)',
        content,
        re.MULTILINE | re.DOTALL
    )
    if not params_section:
        print(f"Warning: No Parameters section found in {template_path}")
        return set()

    # Extract parameter names (must be valid CloudFormation parameter names)
    param_names = re.findall(
        r'^\s+([A-Za-z0-9]+)\s*:',  # Only allow alphanumeric parameter names
        params_section.group(1),
        re.MULTILINE
    )

    if not param_names:
        print(f"Warning: Parameters section empty in {template_path}")

    print(f"Found parameters in {template_path}: {', '.join(param_names)}")
    return set(param_names)

def filter_parameters_file(template_path, parameters_path):
    """Filter parameters.json to only keep parameters defined in the template"""
    # Get allowed parameters from template
    allowed_params = read_template_parameters(template_path)

    # Read current parameters
    with open(parameters_path) as f:
        params_data = json.load(f)

    if 'Parameters' not in params_data:
        print(f"Error: {parameters_path} has no 'Parameters' object")
        return False

    # Filter parameters
    original_count = len(params_data['Parameters'])
    params_data['Parameters'] = {
        k: v for k, v in params_data['Parameters'].items()
        if k in allowed_params
    }
    removed_count = original_count - len(params_data['Parameters'])

    # Write cleaned parameters back
    with open(parameters_path, 'w') as f:
        json.dump(params_data, f, indent=4)

    print(f"Removed {removed_count} parameters not in template")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_parameters.py <template_path> <parameters_path>")
        sys.exit(1)

    template_path = Path(sys.argv[1])
    parameters_path = Path(sys.argv[2])

    if not template_path.exists():
        print(f"Error: Template file {template_path} not found")
        sys.exit(1)

    if not parameters_path.exists():
        print(f"Error: Parameters file {parameters_path} not found")
        sys.exit(1)

    success = filter_parameters_file(template_path, parameters_path)
    sys.exit(0 if success else 1)
