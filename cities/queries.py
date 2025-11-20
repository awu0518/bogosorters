"""
This file deals with our city-level data.
"""
from random import randint
import time
import data.db_connect as dbc
import validation

MIN_ID_LEN = 1
CITY_COLLECTION = 'cities'

ID = 'id'
NAME = 'name'
STATE_CODE = 'state_code'

# Cache configuration
CACHE_MAX_SIZE = 100  # Maximum number of cities to cache
CACHE_EXPIRY_SECONDS = 300  # 5 minutes
city_cache = {}  # {city_name: {'data': city_data, 'timestamp': time}}

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


def _is_cache_entry_valid(city_name: str) -> bool:
    """Check if a specific cache entry is still valid."""
    if city_name not in city_cache:
        return False
    current_time = time.time()
    valid_time = current_time - city_cache[city_name]['timestamp']
    return valid_time < CACHE_EXPIRY_SECONDS


def _evict_oldest_cache_entry():
    """Remove the oldest cache entry when cache is full."""
    if not city_cache:
        return
    keys = city_cache.keys()
    oldest_key = min(keys, key=lambda k: city_cache[k]['timestamp'])
    del city_cache[oldest_key]


def _cache_city(city_name: str, city_data: dict):
    """Add a city to cache, evicting old entries if necessary."""
    if len(city_cache) >= CACHE_MAX_SIZE:
        _evict_oldest_cache_entry()
    city_cache[city_name] = {
        'data': dict(city_data),  # Store a copy
        'timestamp': time.time()
    }


def _invalidate_cache_entry(city_name: str):
    """Remove a specific city from cache."""
    if city_name in city_cache:
        del city_cache[city_name]


def num_cities() -> int:
    return len(read())


def read() -> dict:
    """
    Return all cities using cache-first approach.
    """
    # For bulk read, we'll still go to database to ensure freshness
    # but cache individual entries for subsequent read_one calls
    cities = dbc.read_dict(CITY_COLLECTION, key=NAME)
    # Cache each city individually
    for city_name, city_data in cities.items():
        _cache_city(city_name, city_data)
    return cities


def read_paginated(page: int = 1,
                   limit: int = 50,
                   sort_by: str = NAME,
                   order: str = 'asc') -> dict:
    """
    Return paginated cities list with metadata.
    """
    cond = isinstance(order, str) and order.lower() == 'desc'
    direction = -1 if cond else 1
    return dbc.find_paginated(
        collection=CITY_COLLECTION,
        db=dbc.SE_DB,
        sort=[(sort_by, direction)],
        page=page,
        limit=limit,
        no_id=True
    )


def create(flds: dict) -> str:
    # Validate input
    validation.validate_required_fields(flds, [NAME, STATE_CODE])
    validation.validate_string_length(flds[NAME], 'name', max_length=100)
    validation.validate_string_length(
        flds[STATE_CODE], 'state_code', max_length=2
    )

    new_id = dbc.create(CITY_COLLECTION, flds)
    # Invalidate cache entry if it exists (unlikely but possible)
    city_name = flds.get(NAME)
    if city_name:
        _invalidate_cache_entry(city_name)
    return str(new_id.inserted_id)


def delete(name: str, state_code: str) -> bool:
    ret = dbc.delete(CITY_COLLECTION, {NAME: name, STATE_CODE: state_code})
    if ret < 1:
        raise ValueError(f'City not found: {name}, {state_code}')
    # Invalidate cache entry
    _invalidate_cache_entry(name)
    return ret


def read_one(city_id: str) -> dict:
    """
    Retrieve a single city by ID with cache-first lookup.
    Returns a copy of the city data.
    """
    # Check cache first
    if _is_cache_entry_valid(city_id):
        return dict(city_cache[city_id]['data'])  # Return a copy
    # Cache miss - fetch from database
    cities = read()
    if city_id not in cities:
        raise ValueError(f'No such city: {city_id}')
    city_data = cities[city_id]
    _cache_city(city_id, city_data)
    return dict(city_data)


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
    # If updating the name, we need to handle the key change
    if NAME in flds and flds[NAME] != city_id:
        # Delete old record and create new one with updated name
        old_city = cities[city_id].copy()
        old_city.update(flds)
        delete(city_id, old_city.get(STATE_CODE, ''))
        create(old_city)
        _invalidate_cache_entry(city_id)
    else:
        # Regular update
        dbc.update(CITY_COLLECTION, {NAME: city_id}, flds)
        _invalidate_cache_entry(city_id)
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
        cond = city_data.get(STATE_CODE, '').lower() != state_code.lower()
        if state_code and cond:
            match = False
        if match:
            results[city_name] = city_data
    return results
