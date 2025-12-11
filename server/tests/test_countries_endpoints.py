"""
Basic endpoint tests for countries endpoints.
Mirrors the lean cities endpoint coverage: list, create, delete, search, validation.
"""
from http.client import BAD_REQUEST, CREATED, OK
from unittest.mock import patch
import json
import pytest

import server.endpoints as ep
import countries.queries as ctq


@pytest.fixture
def client():
    """Fixture to provide a test client for the Flask app."""
    return ep.app.test_client()


@pytest.fixture
def sample_country():
    return {"name": "Testland", "iso_code": "TL"}


def test_get_countries_success(client):
    with patch.object(ctq, "read") as mock_read:
        mock_countries = {
            "USA": {"name": "USA", "iso_code": "US"},
            "Canada": {"name": "Canada", "iso_code": "CA"},
        }
        mock_read.return_value = mock_countries

        resp = client.get(ep.COUNTRIES_EP)
        data = resp.get_json()

        assert resp.status_code == OK
        assert ep.COUNTRIES_RESP in data
        assert data["count"] == 2
        assert data[ep.COUNTRIES_RESP] == mock_countries


def test_create_country_success(client, sample_country):
    with patch.object(ctq, "create") as mock_create:
        mock_create.return_value = "507f1f77bcf86cd799439011"

        resp = client.post(
            ep.COUNTRIES_EP,
            data=json.dumps(sample_country),
            content_type="application/json",
        )
        data = resp.get_json()

        assert resp.status_code == CREATED
        assert ep.MESSAGE in data
        assert "created successfully" in data[ep.MESSAGE]
        assert data["id"] == "507f1f77bcf86cd799439011"


def test_delete_country_success(client):
    with patch.object(ctq, "delete") as mock_delete:
        mock_delete.return_value = True

        resp = client.delete(f"{ep.COUNTRIES_EP}/Testland")
        data = resp.get_json()

        assert resp.status_code == OK
        assert ep.MESSAGE in data
        assert "Testland deleted successfully" in data[ep.MESSAGE]


def test_search_countries_by_name(client):
    with patch.object(ctq, "search") as mock_search:
        mock_results = [
            {"name": "France", "iso_code": "FR"},
            {"name": "Finland", "iso_code": "FI"},
        ]
        mock_search.return_value = mock_results

        resp = client.get(f"{ep.COUNTRIES_SEARCH_EP}?name=F")
        data = resp.get_json()

        assert resp.status_code == OK
        assert ep.COUNTRIES_RESP in data
        assert data["count"] == 2
        assert data[ep.COUNTRIES_RESP] == mock_results


def test_create_country_missing_name(client):
    invalid_country = {"iso_code": "XX"}
    with patch.object(ctq, "create") as mock_create:
        mock_create.side_effect = ValueError("Missing required field: name")

        resp = client.post(
            ep.COUNTRIES_EP,
            data=json.dumps(invalid_country),
            content_type="application/json",
        )
        data = resp.get_json()

        assert resp.status_code == BAD_REQUEST
        assert "Missing required field: name" in data.get("error", "")
