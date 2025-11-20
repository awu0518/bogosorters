"""
This file deals with our country-level data.
"""
from random import randint
from typing import Optional
import data.db_connect as dbc
import validation

MIN_ID_LEN = 1
COUNTRY_COLLECTION = 'countries'

ID = 'id'
NAME = 'name'
ISO_CODE = 'iso_code'

SAMPLE_COUNTRY = {
    NAME: 'United States',
    ISO_CODE: 'US',
}

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
    return len(read())

def read() -> dict:
    """Read all countries from MongoDB as a dictionary."""
    return dbc.read_dict(COUNTRY_COLLECTION, key=NAME)

def read_paginated(page: int = 1, limit: int = 50, sort_by: str = NAME, order: str = 'asc') -> dict:
    """
    Return paginated countries list with metadata.
    """
    direction = -1 if isinstance(order, str) and order.lower() == 'desc' else 1
    return dbc.find_paginated(
        collection=COUNTRY_COLLECTION,
        db=dbc.SE_DB,
        sort=[(sort_by, direction)],
        page=page,
        limit=limit,
        no_id=True
    )

def read_one(country_id: str) -> dict:
    """
    Retrieve a single country by ID.
    Returns a copy of the country data.
    """
    countries = read()
    if country_id not in countries:
        raise ValueError(f'No such country: {country_id}')
    return dict(countries[country_id])

def find_by_iso_code(iso_code: str) -> Optional[dict]:
    """
    Find a country by its ISO code (case-insensitive).
    Returns a copy of the country data if found, otherwise None.
    """
    if not isinstance(iso_code, str) or not iso_code:
        return None
    target = iso_code.strip().lower()
    countries = read()
    for rec in countries.values():
        code = rec.get(ISO_CODE)
        if isinstance(code, str) and code.lower() == target:
            return dict(rec)
    return None

def create(flds: dict) -> str:
    # Validate input
    validation.validate_required_fields(flds, [NAME, ISO_CODE])
    validation.validate_string_length(flds[NAME], 'name', max_length=100)
    validation.validate_string_length(flds[ISO_CODE], 'iso_code', max_length=3)

    new_id = dbc.create(COUNTRY_COLLECTION, flds)
    return str(new_id.inserted_id)

def delete(country_id: str) -> bool:
    countries = read()
    if country_id not in countries:
        raise ValueError(f'No such country: {country_id}')
    ret = dbc.delete(COUNTRY_COLLECTION, {NAME: country_id})
    if ret < 1:
        raise ValueError(f'Country not found: {country_id}')
    return True

def update(country_id: str, flds: dict) -> bool:
    """
    Update an existing country with new field values.
    Returns True on success.
    """
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    countries = read()
    if country_id not in countries:
        raise ValueError(f'No such country: {country_id}')
    dbc.update(COUNTRY_COLLECTION, {NAME: country_id}, flds)
    return True

def search(name: str = None, iso_code: str = None) -> dict:
    """
    Search countries by name and/or ISO code (case-insensitive).
    
    Args:
        name: Country name substring to search for
        iso_code: ISO code to filter by
    
    Returns:
        Dictionary of matching countries
    """
    countries = read()
    results = {}
    
    for country_name, country_data in countries.items():
        match = True
        
        if name and name.lower() not in country_data.get(NAME, '').lower():
            match = False
        
        if iso_code and country_data.get(ISO_CODE, '').lower() != iso_code.lower():
            match = False
        
        if match:
            results[country_name] = country_data
    
    return results