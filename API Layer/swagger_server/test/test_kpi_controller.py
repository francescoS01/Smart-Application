# coding: utf-8
"""
    Tests related to kpi endpoints
"""

import pytest
import requests

@pytest.fixture
def kpi():
    k = {
            "category": "Quality and Production Output",
            "description": "The number of production cycles that meet quality standards and do not produce defective items.",
            "formula": None,
            "nameID": "good_cycles",
            "relationNumber": 25,
            "unit": "units"
    }
    return k

@pytest.mark.skip(reason='Not implemented')
def test_kpi_post(client, login):
    headers = {'Authorization':login,'kpiFilter':'power'}
    #TODO: request body?
    response = client.post('/KPI', headers=headers)
    assert response.status_code == 201

def test_kpi_get(client, login, kpi):
    headers = {'Authorization':login}
    response = client.get('/KPI', headers=headers)
    assert response.status_code == 200
    assert len(response.json) > 0
    assert kpi in response.json

@pytest.mark.skip(reason="Doesn't return 400 with strings")
def test_kpi_get_inv_params(client, login):
    headers = {'Authorization':login,'kpiFilter':'foo'}
    response = client.get('/KPI', headers=headers)
    assert response.status_code == 400

def test_kpi_id_get(client, login, kpi):
    headers = {'Authorization':login}
    response = requests.get('https://localhost/KPI/good_cycles', headers=headers, verify=False)
    assert response.status_code == 200
    assert response.json()[0] == kpi

def test_kpi_id_get_not_found(login):
    headers = {'Authorization':login}
    response = requests.get('https://localhost/KPI/foo/', headers=headers, verify=False)
    assert response.status_code == 404

@pytest.mark.order(after="test_machine_data_controller.py::test_machine_post", before="test_machine_data_controller.py::test_machine_delete")
def test_kpi_id_machines_get(client, login, test_machine):
    headers = {'Authorization':login}
    response = requests.get('https://localhost/KPI/good_cycles/machines', headers=headers, verify=False)
    assert response.status_code == 200
    assert "ids" in response.json()
    assert "names" in response.json()
    assert test_machine['name'] in response.json()['names']
    assert test_machine['id'] in response.json()['ids']

def test_kpi_id_machines_get_not_found(client, login):
    headers = {'Authorization':login}
    response = requests.get('https://localhost/KPI/foo/machines', headers=headers, verify=False)
    assert response.status_code == 404

@pytest.mark.skip(reason='Waiting bugfix')
def test_kpi_id_machine_kpi_values_get(client, login, test_machine):
    headers = {'Authorization':login,'aggregationOp':'sum', 'startDate':'2000-01-01', 'endDate':'2024-12-31'}
    response = requests.get('https://localhost/KPI/good_cycles/'+str(test_machine['id'])+'/values', headers=headers, verify=False)
    assert response.status_code == 200
    #TODO: add check after post is implemented

@pytest.mark.parametrize('param',({'startDate':'tomorrow'},{'endDate':'204-01-01 08:00:00'},
                                  {'aggregationOp':'integral'},{'aggregationInterval':'foo'}))
def test_kpi_id_machine_kpi_values_get_inv_params(client, login, param, test_machine):
    headers = {'Authorization':login}
    headers.update(param)
    response = requests.get('https://localhost/KPI/good_cycles/'+str(test_machine['id'])+'/values', headers=headers, verify=False)
    assert response.status_code == 400
    
def test_kpi_id_machine_kpi_values_not_found(login, test_machine):
    headers = {'Authorization':login,'aggregationOp':'sum','aggregationInterval':'day','startDate':'2023-01-01','endDate':'2023-10-01'}
    response = requests.get('https://localhost/KPI/foo/'+str(test_machine['id'])+'/values', headers=headers, verify=False)
    assert response.status_code == 404   