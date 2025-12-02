"""
Tests for bulk operations in countries module.
"""
import pytest
import countries.queries as cq


@pytest.fixture(scope='function')
def clear_cache():
    cq.country_cache.clear()
    cq._next_id = 1
    yield
    cq.country_cache.clear()


def test_bulk_create_success(clear_cache):
    """Test creating multiple countries at once"""
    records = [
        {cq.NAME: "Narnia", cq.ISO_CODE: "NA"},
        {cq.NAME: "Oz", cq.ISO_CODE: "OZ"},
        {cq.NAME: "Wonderland", cq.ISO_CODE: "WL"}
    ]
    result = cq.bulk_create(records)
    assert result['success'] == 3
    assert result['failed'] == 0
    assert len(result['ids']) == 3
    assert len(result['errors']) == 0
    assert cq.num_countries() == 3


def test_bulk_create_with_failures(clear_cache):
    """Test bulk create with some invalid records"""
    records = [
        {cq.NAME: "Narnia", cq.ISO_CODE: "NA"},  # Valid
        {cq.NAME: "Oz"},  # Missing ISO_CODE
        {cq.NAME: "Wonderland", cq.ISO_CODE: "WL"}  # Valid
    ]
    result = cq.bulk_create(records)
    assert result['success'] == 2
    assert result['failed'] == 1
    assert len(result['ids']) == 2
    assert len(result['errors']) == 1
    assert result['errors'][0]['index'] == 1


def test_bulk_create_invalid_input(clear_cache):
    """Test bulk create with invalid input type"""
    with pytest.raises(ValueError, match="Records must be a list"):
        cq.bulk_create({"not": "a list"})


def test_bulk_update_success(clear_cache):
    """Test updating multiple countries at once"""
    # Create some countries first
    cq.create({cq.NAME: "Narnia", cq.ISO_CODE: "NA"})
    cq.create({cq.NAME: "Oz", cq.ISO_CODE: "OZ"})

    updates = [
        {"id": "1", "fields": {cq.ISO_CODE: "NAR"}},
        {"id": "2", "fields": {cq.ISO_CODE: "OZZ"}}
    ]
    result = cq.bulk_update(updates)
    assert result['success'] == 2
    assert result['failed'] == 0
    assert len(result['errors']) == 0


def test_bulk_update_with_failures(clear_cache):
    """Test bulk update with some failures"""
    cq.create({cq.NAME: "Narnia", cq.ISO_CODE: "NA"})

    updates = [
        {"id": "1", "fields": {cq.ISO_CODE: "NAR"}},  # Valid
        {"id": "999", "fields": {cq.ISO_CODE: "XX"}},  # Non-existent
    ]
    result = cq.bulk_update(updates)
    assert result['success'] == 1
    assert result['failed'] == 1
    assert len(result['errors']) == 1
    assert result['errors'][0]['id'] == "999"


def test_bulk_update_invalid_input(clear_cache):
    """Test bulk update with invalid input type"""
    with pytest.raises(ValueError, match="Updates must be a list"):
        cq.bulk_update({"not": "a list"})


def test_bulk_delete_success(clear_cache):
    """Test deleting multiple countries at once"""
    cq.create({cq.NAME: "Narnia", cq.ISO_CODE: "NA"})
    cq.create({cq.NAME: "Oz", cq.ISO_CODE: "OZ"})
    cq.create({cq.NAME: "Wonderland", cq.ISO_CODE: "WL"})

    result = cq.bulk_delete(["1", "2"])
    assert result['success'] == 2
    assert result['failed'] == 0
    assert cq.num_countries() == 1


def test_bulk_delete_with_failures(clear_cache):
    """Test bulk delete with some failures"""
    cq.create({cq.NAME: "Narnia", cq.ISO_CODE: "NA"})

    result = cq.bulk_delete(["1", "999"])
    assert result['success'] == 1
    assert result['failed'] == 1
    assert len(result['errors']) == 1
    assert result['errors'][0]['id'] == "999"


def test_bulk_delete_invalid_input(clear_cache):
    """Test bulk delete with invalid input type"""
    with pytest.raises(ValueError, match="IDs must be a list"):
        cq.bulk_delete({"not": "a list"})
