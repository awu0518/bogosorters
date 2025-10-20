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