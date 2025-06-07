import os
import pandas as pd
import json

def read_instructions(file_name: str) -> str:
    """Read and return the contents of a file.

    Args:
        file_path (str): The path to the file to be read.

    Returns:
        str: The complete contents of the file as a string.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        IOError: If there are issues reading the file.
    """
    with open(f"prompt instructions/{file_name}", "r") as file:
        return file.read()


# def search_products(query: str, max_results: int = 5) -> list[dict]:
#     params = {
#         "q": query,
#         "engine": "google",
#         "tbm": "shop",  # Shopping tab
#         "api_key": "YOUR_SERPAPI_KEY"
#     }
#     search = GoogleSearch(params)
#     results = search.get_dict()
#
#     return [
#         {
#             "title": item.get("title"),
#             "price": item.get("extracted_price"),
#             "url": item.get("link"),
#             "image": item.get("thumbnail")
#         }
#         for item in results.get("shopping_results", [])[:max_results]
#     ]

import pandas as pd
import re


def parse_failure_modes_to_dataframe(json_data):
    """Convert failure mode strings to DataFrame"""

    failure_modes_data = []

    for fm_string in json_data.failure_modes:
        # Parse each field using regex
        parsed = {}

        # Extract fields
        parsed['id'] = fm_string.id
        parsed['failure_mode'] = fm_string.failure_mode
        parsed['failure_cause'] = fm_string.failure_cause
        parsed['failure_effect'] = fm_string.failure_effect
        parsed['mitigation'] = fm_string.mitigation
        parsed['severity'] = fm_string.severity
        parsed['impact'] = fm_string.impact
        parsed['priority'] = fm_string.priority

        # parsed['name'] = re.search(r"name='([^']*)'", fm_string).group(1)
        # parsed['description'] = re.search(r"description='([^']*)'", fm_string).group(1)
        # parsed['severity'] = re.search(r"severity=<Severity\.\w+: '(\w+)'>", fm_string).group(1)
        # parsed['priority'] = int(re.search(r"priority=(\d+)", fm_string).group(1))

        failure_modes_data.append(parsed)

    return pd.DataFrame(failure_modes_data)