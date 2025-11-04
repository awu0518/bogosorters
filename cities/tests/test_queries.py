"""
Tests for cities.queries module
"""
from unittest.mock import patch
import pytest

import cities.queries as cq

@pytest.fixture(scope='function')
def mock_randint():
    """Fixture to mock randint for predictable testing"""
    with patch('cities.queries.randint') as mock_rand:
        yield mock_rand


def test_db_connect_success(mock_randint):
    """Test db_connect with guaranteed success"""
    mock_randint.return_value = 1 
    
    result = cq.db_connect(1)
    assert result is True
    mock_randint.assert_called_once_with(1, 1)


def test_db_connect_failure(mock_randint):
    """Test db_connect with guaranteed failure"""
    mock_randint.return_value = 1
    
    result = cq.db_connect(2)
    assert result is False
    mock_randint.assert_called_once_with(1, 2)

# create tests
@pytest.fixture(scope='function')
def clear_city_cache():
    """Fixture to clear city_cache before each test"""
    cq.city_cache.clear()
    yield
    cq.city_cache.clear()

@pytest.fixture(scope='function')
def temp_city(clear_city_cache):
    """Create a temporary city and yield its id"""
    flds = {cq.NAME: "Boston", cq.STATE_CODE: "MA"}
    cid = cq.create(flds)
    return cid

def test_create_success(clear_city_cache):
    """Test create function with valid input"""
    flds = {cq.NAME: "New York", cq.STATE_CODE: "NY"}
    
    result = cq.create(flds)
    
    assert result == "1"  # First city should get ID "1"
    assert cq.city_cache["1"] == flds
    assert cq.num_cities() == 1

def test_create_multiple_cities(clear_city_cache):
    """Test creating multiple cities"""
    city1 = {cq.NAME: "New York", cq.STATE_CODE: "NY"}
    city2 = {cq.NAME: "Los Angeles", cq.STATE_CODE: "CA"}
    
    id1 = cq.create(city1)
    id2 = cq.create(city2)
    
    assert id1 == "1"
    assert id2 == "2"
    assert cq.city_cache["1"] == city1
    assert cq.city_cache["2"] == city2
    assert cq.num_cities() == 2

@patch('cities.queries.db_connect', return_value=True, autospec=True)
def test_delete(mock_db_connect, temp_city):
    cq.delete(temp_city)
    assert temp_city not in cq.read()

@pytest.mark.skip('revive once all functions are cutover!')
def test_read(temp_city):
    cities = cq.read()
    assert isinstance(cities, dict)
    assert temp_city in cities

def test_read_one_success(temp_city):
    """Test read_one function with valid city ID"""
    city = cq.read_one(temp_city)
    assert city[cq.NAME] == "Boston"
    assert city[cq.STATE_CODE] == "MA"


def test_read_one_raises_on_missing(clear_city_cache):
    """Test read_one raises error for non-existent city"""
    with pytest.raises(ValueError, match="No such city"):
        cq.read_one("999")


def test_read_one_returns_copy(temp_city):
    """Verify that modifying the returned dict doesn't affect the cache"""
    city = cq.read_one(temp_city)
    city[cq.NAME] = "Modified Name"
    # Original should be unchanged
    assert cq.read_one(temp_city)[cq.NAME] == "Boston"

def test_update_city_success(temp_city):
    """Test update function with valid input"""
    # Update the city's name
    new_data = {cq.NAME: "New Boston"}
    assert cq.update(temp_city, new_data) is True
    updated_city = cq.read()[temp_city]
    assert updated_city[cq.NAME] == "New Boston"
    # STATE_CODE should remain unchanged
    assert updated_city[cq.STATE_CODE] == "MA"


def test_update_city_raises_on_missing(clear_city_cache):
    """Test update raises error for non-existent city"""
    with pytest.raises(ValueError, match="No such city"):
        cq.update("999", {cq.NAME: "Ghost City"})


def test_update_city_raises_on_bad_type(temp_city):
    """Test update raises error for invalid input type"""
    with pytest.raises(ValueError, match="Bad type"):
        cq.update(temp_city, ["not", "a", "dict"])