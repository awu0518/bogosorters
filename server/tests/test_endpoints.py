from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch

import pytest

import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()


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