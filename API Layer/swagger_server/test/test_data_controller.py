# coding: utf-8
"""
    Tests related to sensor data endpoints
"""

import pytest
import time
import requests

@pytest.fixture
def test_data():
    r = {
            "kpi": "good_cycles",
            "valueSeries": [
                42.0
            ]
        }
    return r

@pytest.mark.order("first", after="test_machine_data_controller.py::test_machine_post", before="test_machine_data_controller.py::test_machine_delete")
def test_data_post(client, login, test_machine, test_data):
    headers = {'Authorization':login,'id':str(test_machine['id']),'kpi':'good_cycles','aggregationType':'sum',
               'values':'42.0'}
    response = requests.post('https://localhost/data/good_cycles/'+str(test_machine['id']), headers=headers, verify=False)
    test_machine['status'] = 'operational'
    assert response.status_code == 200
    time.sleep(2)

@pytest.mark.order("second", after="test_data_post", before="test_machine_data_controller.py::test_machine_delete")
def test_data_raw_get(client, login, test_data, test_machine):
    headers = {'Authorization':login,'machines':str(test_machine['id']),'dataTypes':'good_cycles','aggregationSelector':'sum'}
    response = client.get('/data/raw', headers=headers)
    assert response.status_code == 200
    assert len(response.json) > 0
    for k in test_data:
        assert k in response.json[0]
        assert test_data[k] == response.json[0][k]

@pytest.mark.parametrize('param',({'machines':'foo'},{'aggregationSelector':'foo'},{'from':'15'},{'to':'tomorrow'}))
def test_data_raw_get_inv_params(client, login, param):
    headers = {'Authorization':login}
    headers.update(param)
    response = client.get('/data/raw', headers=headers)
    assert response.status_code == 400

def test_data_raw_get_not_auth(client, login):
    response = client.get('/data/raw')
    assert response.status_code == 401

@pytest.mark.skip(reason='WIP')
def test_data_preprocessed_get(client, login, test_machine, test_data):
    headers = {'Authorization':login,'machines':str(test_machine['id']),'dataTypes':'good_cycles','aggregationSelector':'sum'}
    response = client.get('/data/preprocessed', headers=headers)
    assert response.status_code == 200
    for k in test_data:
        assert k in response.json[0]
        assert test_data[k] == response.json[0][k]