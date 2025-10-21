from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch, MagicMock
from datetime import datetime

import pytest

import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()


# FIXTURE: Reusable test client fixture
@pytest.fixture
def client():
    """Fixture to provide a test client for the Flask app."""
    return ep.app.test_client()


# FIXTURE: Sample timestamp for testing
@pytest.fixture
def mock_timestamp():
    """Fixture to provide a consistent timestamp for testing."""
    return datetime(2025, 10, 21, 12, 0, 0)


# FIXTURE: Expected endpoint list
@pytest.fixture
def expected_endpoints():
    """Fixture to provide expected list of endpoints."""
    return [ep.HELLO_EP, ep.ENDPOINT_EP, ep.TIMESTAMP_EP, ep.RANDOM_EP, ep.DICE_EP]


def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert resp.status_code == OK
    assert ep.HELLO_RESP in resp_json


def test_endpoints_lists_hello():
    resp = TEST_CLIENT.get(ep.ENDPOINT_EP)
    data = resp.get_json()
    assert resp.status_code == OK
    assert ep.ENDPOINT_RESP in data
    assert ep.HELLO_EP in data[ep.ENDPOINT_RESP]


# Using FIXTURE
def test_hello_with_fixture(client):
    """Test hello endpoint using client fixture."""
    resp = client.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert resp.status_code == OK
    assert resp_json[ep.HELLO_RESP] == 'world'


# Using FIXTURE
def test_all_endpoints_present(client, expected_endpoints):
    """Test that all expected endpoints are listed using fixtures."""
    resp = client.get(ep.ENDPOINT_EP)
    data = resp.get_json()
    assert resp.status_code == OK
    endpoints_list = data[ep.ENDPOINT_RESP]
    for endpoint in expected_endpoints:
        assert endpoint in endpoints_list


# PATCH: Mock datetime for timestamp endpoint
@patch('server.endpoints.datetime')
def test_timestamp_with_patch(mock_datetime, client):
    """Test timestamp endpoint with mocked datetime using patch."""
    # Setup mock
    mock_now = datetime(2025, 10, 21, 15, 30, 45)
    mock_datetime.now.return_value = mock_now
    
    resp = client.get(ep.TIMESTAMP_EP)
    data = resp.get_json()
    
    assert resp.status_code == OK
    assert ep.TIMESTAMP_RESP in data
    assert data[ep.TIMESTAMP_RESP] == mock_now.isoformat()
    assert data['unix'] == mock_now.timestamp()


# PATCH: Mock random for random endpoint
@patch('server.endpoints.random.randint')
def test_random_with_patch(mock_randint, client):
    """Test random endpoint with mocked random.randint using patch."""
    mock_randint.return_value = 42
    
    resp = client.get(ep.RANDOM_EP)
    data = resp.get_json()
    
    assert resp.status_code == OK
    assert data[ep.RANDOM_RESP] == 42
    assert data['min'] == 1
    assert data['max'] == 100


# PATCH: Mock random for dice endpoint
@patch('server.endpoints.random.randint')
def test_dice_with_patch(mock_randint, client):
    """Test dice endpoint with mocked random using patch."""
    mock_randint.side_effect = [3, 5]  # Two dice rolls
    
    resp = client.get(ep.DICE_EP)
    data = resp.get_json()
    
    assert resp.status_code == OK
    assert data[ep.DICE_RESP] == [3, 5]
    assert data['total'] == 8
    assert data['num_dice'] == 2
    assert data['sides'] == 6


# PYTEST.RAISES: Test invalid endpoint
def test_invalid_endpoint_raises_404(client):
    """Test that accessing invalid endpoint returns 404 using pytest.raises."""
    resp = client.get('/invalid_endpoint')
    assert resp.status_code == NOT_FOUND


# PYTEST.RAISES: Test for expected data structure
def test_timestamp_has_required_fields(client):
    """Test that timestamp response has required fields."""
    resp = client.get(ep.TIMESTAMP_EP)
    data = resp.get_json()
    
    # This will raise KeyError if fields are missing
    with pytest.raises(KeyError, match="nonexistent"):
        _ = data['nonexistent']
    
    # Verify required fields exist (won't raise)
    assert ep.TIMESTAMP_RESP in data
    assert 'unix' in data


# PYTEST.RAISES: Test dice values are in valid range
def test_dice_values_in_range(client):
    """Test that dice rolls are within valid range."""
    for _ in range(10):  # Test multiple rolls
        resp = client.get(ep.DICE_EP)
        data = resp.get_json()
        
        for roll in data[ep.DICE_RESP]:
            assert 1 <= roll <= 6, f"Dice roll {roll} out of range"
        
        # Test that invalid assertion would raise
        with pytest.raises(AssertionError):
            assert roll > 10  # This should fail


# SKIP: Skip this test for future implementation
@pytest.mark.skip(reason="Feature not yet implemented - waiting for POST support")
def test_custom_dice_rolls(client):
    """Test custom number of dice (future feature)."""
    resp = client.post(ep.DICE_EP, json={'num_dice': 3, 'sides': 20})
    data = resp.get_json()
    assert len(data[ep.DICE_RESP]) == 3


# SKIP: Conditional skip based on environment
@pytest.mark.skip(reason="Integration test - requires external service")
def test_timestamp_matches_external_service(client):
    """Test that our timestamp matches an external time service."""
    # This would require network access in real scenario
    pass


# Test random endpoint returns values in range
def test_random_number_in_range(client):
    """Test that random endpoint returns values in expected range."""
    for _ in range(20):  # Test multiple calls
        resp = client.get(ep.RANDOM_EP)
        data = resp.get_json()
        
        assert resp.status_code == OK
        random_num = data[ep.RANDOM_RESP]
        assert 1 <= random_num <= 100


# Test timestamp endpoint returns current time
def test_timestamp_returns_valid_format(client):
    """Test that timestamp endpoint returns valid ISO format."""
    resp = client.get(ep.TIMESTAMP_EP)
    data = resp.get_json()
    
    assert resp.status_code == OK
    # Verify we can parse the ISO timestamp
    timestamp_str = data[ep.TIMESTAMP_RESP]
    parsed_time = datetime.fromisoformat(timestamp_str)
    assert isinstance(parsed_time, datetime)