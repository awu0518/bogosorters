"""
Tests for countries.queries module
"""
from unittest.mock import patch
import pytest

import countries.queries as cq


# FIXTURE: Clear the cache around each test
@pytest.fixture(scope='function')
def clear_country_cache():
    cq.country_cache.clear()
    yield
    cq.country_cache.clear()


# FIXTURE: Create a temporary country and yield its id
@pytest.fixture(scope='function')
def temp_country(clear_country_cache):
    flds = {cq.NAME: "Freedonia", cq.ISO_CODE: "FD"}
    cid = cq.create(flds)
    return cid


# PATCH via fixture: mock randint used by db_connect
@pytest.fixture(scope='function')
def mock_randint():
    with patch('countries.queries.randint') as mock_rand:
        yield mock_rand


def test_db_connect_success(mock_randint):
    mock_randint.return_value = 1
    assert cq.db_connect(1) is True
    mock_randint.assert_called_once_with(1, 1)


def test_db_connect_failure(mock_randint):
    mock_randint.return_value = 1
    assert cq.db_connect(2) is False
    mock_randint.assert_called_once_with(1, 2)


def test_create_success(clear_country_cache):
    flds = {cq.NAME: "Narnia", cq.ISO_CODE: "NA"}
    new_id = cq.create(flds)
    assert new_id == "1"
    assert cq.country_cache["1"] == flds
    assert cq.num_countries() == 1


def test_create_multiple(clear_country_cache):
    c1 = {cq.NAME: "Narnia", cq.ISO_CODE: "NA"}
    c2 = {cq.NAME: "Oz", cq.ISO_CODE: "OZ"}
    id1 = cq.create(c1)
    id2 = cq.create(c2)
    assert id1 == "1"
    assert id2 == "2"
    assert cq.num_countries() == 2


# WITH RAISES: invalid inputs
def test_create_raises_on_bad_type(clear_country_cache):
    with pytest.raises(ValueError, match="Bad type"):
        cq.create(["not", "a", "dict"])


def test_create_raises_on_missing_name(clear_country_cache):
    with pytest.raises(ValueError, match="Bad value"):
        cq.create({cq.ISO_CODE: "XX"})


def test_delete_success(temp_country):
    assert cq.delete(temp_country) is True
    assert temp_country not in cq.read()


def test_delete_raises_on_missing(clear_country_cache):
    with pytest.raises(ValueError, match="No such country"):
        cq.delete("999")


# SKIP: future feature not implemented yet
@pytest.mark.skip(reason="Feature not yet implemented - update country")
def test_update_country_future_feature():
    pass


# PATCH: patch db_connect directly
@patch('countries.queries.db_connect', return_value=True, autospec=True)
def test_db_connect_patched(mock_db_connect):
    assert cq.db_connect(10) is True
    mock_db_connect.assert_called_once()