"""
This file deals with our city-level data.
"""

MIN_ID_LEN = 1

ID = 'id'
NAME = 'name'
STATE_CODE = 'state_code'

city_cache = { }

# Returns if a given ID is a valid city ID.
def is_valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True

def num_cities() -> int:
    return len(city_cache)
