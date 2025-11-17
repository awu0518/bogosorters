"""
This file deals with our city-level data.
"""
from random import randint
import data.db_connect as dbc

MIN_ID_LEN = 1
CITY_COLLECTION = 'cities'

ID = 'id'
NAME = 'name'
STATE_CODE = 'state_code'

SAMPLE_CITY = {
    NAME: 'New York',
    STATE_CODE: 'NY',
}

# db connection placeholder
def db_connect(success_ratio: int) -> bool:
    """
    Return True if connected, False if not.
    Simulates database connection with configurable success rate.
    
    Returns:
        bool: True if connection succeeds, False otherwise
    """
    return randint(1, success_ratio) % success_ratio == 0

# Returns if a given ID is a valid city ID.
def is_valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True

def num_cities() -> int:
    return len(read())

def read() -> dict:
    return dbc.read_dict(CITY_COLLECTION, key=NAME)

def create(flds: dict) -> str:
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    new_id = dbc.create(CITY_COLLECTION, flds)
    return str(new_id.inserted_id)

def delete(name: str, state_code: str) -> bool:
    ret = dbc.delete(CITY_COLLECTION, {NAME: name, STATE_CODE: state_code})
    if ret < 1:
        raise ValueError(f'City not found: {name}, {state_code}')
    return ret

def read_one(city_id: str) -> dict:
    """
    Retrieve a single city by ID.
    Returns a copy of the city data.
    """
    cities = read()
    if city_id not in cities:
        raise ValueError(f'No such city: {city_id}')
    # return a copy for safety
    return dict(cities[city_id])

def update(city_id: str, flds: dict) -> bool:
    """
    Update an existing city with new field values.
    Returns True on success.
    """
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    cities = read()
    if city_id not in cities:
        raise ValueError(f'No such city: {city_id}')
    dbc.update(CITY_COLLECTION, {NAME: city_id}, flds)
    return True

def search(name: str = None, state_code: str = None) -> dict:
    """
    Search cities by name and/or state_code (case-insensitive).
    
    Args:
        name: City name substring to search for
        state_code: State code to filter by
    
    Returns:
        Dictionary of matching cities
    """
    cities = read()
    results = {}
    
    for city_name, city_data in cities.items():
        match = True
        
        if name and name.lower() not in city_data.get(NAME, '').lower():
            match = False
        
        if state_code and city_data.get(STATE_CODE, '').lower() != state_code.lower():
            match = False
        
        if match:
            results[city_name] = city_data
    
    return results