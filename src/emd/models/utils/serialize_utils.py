import json
import argparse

JSON_DOUBLE_QUOTE_REPLACE = '<!>'


def load_extra_params(string):
    string = string.replace(JSON_DOUBLE_QUOTE_REPLACE,'"')
    try:
        return json.loads(string)
    except json.JSONDecodeError:
        raise argparse.ArgumentTypeError(f"Invalid dictionary format: {string}")

def dump_extra_params(d:dict):
    return json.dumps(d).replace('"', JSON_DOUBLE_QUOTE_REPLACE)
