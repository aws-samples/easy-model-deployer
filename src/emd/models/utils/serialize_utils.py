import json
import argparse
import base64


def load_extra_params(string):
    try:
        # Decode the base64 string back to JSON string
        json_bytes = base64.b64decode(string.encode('utf-8'))
        json_str = json_bytes.decode('utf-8')
        return json.loads(json_str)
    except (base64.binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
        raise argparse.ArgumentTypeError(f"Invalid dictionary format: {string}")


def dump_extra_params(d: dict):
    # Convert dict to JSON string, then encode to base64
    json_str = json.dumps(d)
    json_bytes = json_str.encode('utf-8')
    base64_bytes = base64.b64encode(json_bytes)
    return base64_bytes.decode('utf-8')
