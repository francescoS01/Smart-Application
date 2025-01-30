# coding: utf-8

"""
    Tests related to machineXKPI endpoints
"""

import pytest

def test_machine_xkpi_get(client, login):
    headers = {'Authorization':login}
    response = client.get('/machineXKPI', headers=headers)
    assert response.status_code == 200
    assert len(response.json) > 0
    assert "kpis" in response.json
    assert "machines" in response.json
    assert "relation" in response.json

def test_machine_xkpi_get_not_auth(client):
    response = client.get('/machineXKPI')
    assert response.status_code == 401