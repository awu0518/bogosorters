"""
This file deals with our country-level data.
"""
from random import randint
from typing import Optional

MIN_ID_LEN = 1

ID = 'id'
NAME = 'name'
ISO_CODE = 'iso_code'

country_cache = { }

# db connection placeholder
def db_connect(success_ratio: int) -> bool:
    """
    Return True if connected, False if not.
    Simulates database connection with configurable success rate.
    """
    return randint(1, success_ratio) % success_ratio == 0

# Returns if a given ID is a valid country ID.
def is_valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True

def num_countries() -> int:
    return len(country_cache)

def read() -> dict:
    # shallow copy for safety
    return dict(country_cache)

def read_one(country_id: str) -> dict:
    """
    Retrieve a single country by ID.
    Returns a copy of the country data.
    """
    if country_id not in country_cache:
        raise ValueError(f'No such country: {country_id}')
    # return a copy for safety
    return dict(country_cache[country_id])

def find_by_iso_code(iso_code: str) -> Optional[dict]:
    """
    Find a country by its ISO code (case-insensitive).
    Returns a copy of the country data if found, otherwise None.
    """
    if not isinstance(iso_code, str) or not iso_code:
        return None
    target = iso_code.strip().lower()
    for rec in country_cache.values():
        code = rec.get(ISO_CODE)
        if isinstance(code, str) and code.lower() == target:
            return dict(rec)
    return None

def create(flds: dict) -> str:
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    new_id = str(len(country_cache) + 1)
    country_cache[new_id] = flds
    return new_id

def delete(country_id: str) -> bool:
    if country_id not in country_cache:
        raise ValueError(f'No such country: {country_id}')
    del country_cache[country_id]
    return True

def update(country_id: str, flds: dict) -> bool:
    """
    Update an existing country with new field values.
    Returns True on success.
    """
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    if country_id not in country_cache:
        raise ValueError(f'No such country: {country_id}')
    country_cache[country_id].update(flds)
    return True