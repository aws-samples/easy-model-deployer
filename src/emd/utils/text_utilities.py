import random
import string
import json

from emd.patch_questionary.common_with_help import Choice

def random_suffix(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def normalize(input_str: str) -> str:
    """
    Process a string to only keep valid characters [a-zA-Z][-a-zA-Z0-9]*.
    Converts underscores and dots to hyphens.

    Args:
        input_str: Input string to process

    Returns:
        Processed string with only valid characters
    """
    if not input_str:
        return ""

    # First replace _ and . with -
    processed = input_str.replace("_", "-").replace(".", "-")

    # Build result string character by character
    result = []

    # First character must be [a-zA-Z]
    for i, char in enumerate(processed):
        if i == 0:
            if char.isalpha():
                result.append(char)
        else:
            # Subsequent characters can be [-a-zA-Z0-9]
            if char.isalnum() or char == "-":
                result.append(char)

    return "".join(result)

def enum_to_choices(enum):
    return [
        Choice(
            title=json.loads(item.value.replace("'", '"'))["title"],
            description=json.loads(item.value.replace("'", '"'))["description"],
        )
        for item in enum
    ]

def enum_to_strings(enum):
    return [json.loads(item.value.replace("'", '"'))["title"] for item in enum]
