"""
Basic tests for cities endpoints in the Flask API.
Tests essential CRUD operations and basic functionality.
"""

from http.client import (
    BAD_REQUEST,
    CREATED,
    NOT_FOUND,
    OK,
    INTERNAL_SERVER_ERROR,
)

from unittest.mock import patch
import pytest
import json

import server.endpoints as ep
import cities.queries as cq

# Test client fixture
@pytest.fixture
def client():
    """Fixture to provide a test client for the Flask app."""
    return ep.app.test_client()

# Sample city data for testing
@pytest.fixture
def sample_city():
    """Fixture providing sample city data."""
    return {
        'name': 'Test City',
        'state_code': 'TC'
    }


def test_get_cities_success(client):
    """Test successful retrieval of cities."""
    with patch.object(cq, 'read') as mock_read:
        mock_cities = {
            'New York': {'name': 'New York', 'state_code': 'NY'},
            'Boston': {'name': 'Boston', 'state_code': 'MA'}
        }
        mock_read.return_value = mock_cities
        
        resp = client.get(ep.CITIES_EP)
        data = resp.get_json()
        
        assert resp.status_code == OK
        assert ep.CITIES_RESP in data
        assert 'count' in data
        assert data['count'] == 2
        assert data[ep.CITIES_RESP] == mock_cities


def test_create_city_success(client, sample_city):
    """Test successful city creation."""
    with patch.object(cq, 'create') as mock_create:
        mock_create.return_value = "507f1f77bcf86cd799439011"  # Mock ObjectId
        
        resp = client.post(
            ep.CITIES_EP,
            data=json.dumps(sample_city),
            content_type='application/json'
        )
        data = resp.get_json()
        
        assert resp.status_code == CREATED
        assert ep.MESSAGE in data
        assert 'created successfully' in data[ep.MESSAGE]
        assert 'id' in data
        assert data['id'] == "507f1f77bcf86cd799439011"


def test_delete_city_success(client):
    """Test successful city deletion."""
    with patch.object(cq, 'delete') as mock_delete:
        mock_delete.return_value = 1  # Number of deleted records
        
        resp = client.delete(f'{ep.CITIES_EP}/Test City?state_code=TC')
        data = resp.get_json()
        
        assert resp.status_code == OK
        assert ep.MESSAGE in data
        assert 'Test City deleted successfully' in data[ep.MESSAGE]


def test_search_cities_by_name(client):
    """Test city search by name."""
    with patch.object(cq, 'search') as mock_search:
        mock_results = [
            {'name': 'New York', 'state_code': 'NY'},
            {'name': 'New Orleans', 'state_code': 'LA'}
        ]
        mock_search.return_value = mock_results
        
        resp = client.get(f'{ep.CITIES_SEARCH_EP}?name=New')
        data = resp.get_json()
        
        assert resp.status_code == OK
        assert ep.CITIES_RESP in data
        assert 'count' in data
        assert data['count'] == 2
        assert data[ep.CITIES_RESP] == mock_results


def test_create_city_missing_name(client):
    """Test city creation with missing name field."""
    invalid_city = {'state_code': 'NY'}
    
    with patch.object(cq, 'create') as mock_create:
        mock_create.side_effect = ValueError("Missing required field: name")
        
        resp = client.post(
            ep.CITIES_EP,
            data=json.dumps(invalid_city),
            content_type='application/json'
        )
        data = resp.get_json()
        
        assert resp.status_code == BAD_REQUEST
        assert 'error' in data
        assert 'Missing required field: name' in data['error']