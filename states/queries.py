"""
This file deals with our state-level data.
"""
from random import randint
from typing import Optional
import data.db_connect as dbc
import validation

MIN_ID_LEN = 1
STATE_COLLECTION = 'states'

ID = 'id'
NAME = 'name'
STATE_CODE = 'state_code'
ABBREVIATION = 'abbreviation'  # Alias for state_code
CAPITAL = 'capital'
POPULATION = 'population'

SAMPLE_STATE = {
    NAME: 'New York',
    STATE_CODE: 'NY',
    CAPITAL: 'Albany',
}


def db_connect(success_ratio: int) -> bool:
    """
    Return True if connected, False if not.
    Simulates database connection with configurable success rate.
    Returns:
        bool: True if connection succeeds, False otherwise
    """
    return randint(1, success_ratio) % success_ratio == 0


# Returns if a given ID is a valid state ID.
def is_valid_id(_id: str) -> bool:
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True


def num_states() -> int:
    return len(read())


def read() -> dict:
    """Read all states from MongoDB as a dictionary."""
    return dbc.read_dict(STATE_COLLECTION, key=NAME)


def read_paginated(page: int = 1, limit: int = 50,
                   sort_by: str = NAME, order: str = 'asc') -> dict:
    """
    Return paginated states list with metadata.
    """
    direction = -1 if isinstance(order, str) and order.lower() == 'desc' else 1
    return dbc.find_paginated(
        collection=STATE_COLLECTION,
        db=dbc.SE_DB,
        sort=[(sort_by, direction)],
        page=page,
        limit=limit,
        no_id=True
    )


def read_one(state_id: str) -> dict:
    """
    Retrieve a single state by ID (name).
    Returns a copy of the state data.
    """
    states = read()
    if state_id not in states:
        raise ValueError(f'No such state: {state_id}')
    return dict(states[state_id])


def find_by_state_code(state_code: str) -> Optional[dict]:
    """
    Find a state by its state code (case-insensitive).
    Returns a copy of the state data if found, otherwise None.
    """
    if not isinstance(state_code, str) or not state_code:
        return None
    target = state_code.strip().upper()
    states = read()
    for rec in states.values():
        code = rec.get(STATE_CODE)
        if isinstance(code, str) and code.upper() == target:
            return dict(rec)
    return None


def create(flds: dict) -> str:
    """Create a new state."""
    # Validate required fields
    validation.validate_required_fields(flds, [NAME, STATE_CODE])
    validation.validate_string_length(flds[NAME], 'name',
                                      max_length=100)
    validation.validate_string_length(flds[STATE_CODE], 'state_code',
                                      max_length=2)

    # Validate state_code is exactly 2 characters
    if len(flds[STATE_CODE]) != 2:
        raise ValueError('state_code must be exactly 2 characters')

    # Optional field validation
    if CAPITAL in flds:
        validation.validate_string_length(flds[CAPITAL], 'capital',
                                          max_length=100)

    new_id = dbc.create(STATE_COLLECTION, flds)
    return str(new_id.inserted_id)


def delete(state_id: str) -> bool:
    """Delete a state by ID (name)."""
    states = read()
    if state_id not in states:
        raise ValueError(f'No such state: {state_id}')
    ret = dbc.delete(STATE_COLLECTION, {NAME: state_id})
    if ret < 1:
        raise ValueError(f'State not found: {state_id}')
    return True


def update(state_id: str, flds: dict) -> bool:
    """
    Update an existing state with new field values.
    Returns True on success.
    """
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    states = read()
    if state_id not in states:
        raise ValueError(f'No such state: {state_id}')
    dbc.update(STATE_COLLECTION, {NAME: state_id}, flds)
    return True


def search(name: str = None, state_code: str = None,
           capital: str = None) -> dict:
    """
    Search states by name, state_code, and/or capital (case-insensitive).

    Args:
        name: State name substring to search for
        state_code: State code to filter by (exact match)
        capital: Capital name substring to search for

    Returns:
        Dictionary of matching states
    """
    states = read()
    results = {}

    for state_name, state_data in states.items():
        match = True

        if name and name.lower() not in state_data.get(NAME, '').lower():
            match = False

        if state_code:
            data_code = state_data.get(STATE_CODE, '').upper()
            if data_code != state_code.upper():
                match = False

        if capital:
            data_capital = state_data.get(CAPITAL, '').lower()
            if capital.lower() not in data_capital:
                match = False

        if match:
            results[state_name] = state_data

    return results
