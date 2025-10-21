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