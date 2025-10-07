"""
This file deals with our city-level data.
"""

MIN_ID_LEN = 1

def is_valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True