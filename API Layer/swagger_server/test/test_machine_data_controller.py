# coding: utf-8
"""
    Tests related to machine endpoints
"""

import pytest
import requests


@pytest.mark.order("first")
def test_machine_post(client, login, test_machine):
    headers = {'Authorization':login, 'name':'test', 'productionLine':0, 'factory': 'test', 'machineType':'Testing Machine'}
    response = client.post('/machine', headers=headers)
    assert response.status_code == 201
    machine_id = int(response.data)
    test_machine['id'] = machine_id
    headers = {'Authorization':login, 'machines':machine_id}
    response = client.get('/machine', headers=headers)
    assert response.status_code == 200
    for k in test_machine:
        assert k in response.json[0]
        assert test_machine[k] == response.json[0][k]

@pytest.mark.order(after="test_data_controller.py::test_data_post")
def test_machine_get(client, login, test_machine):
    headers = {'Authorization':login, 'machines':str(test_machine['id'])}
    response = client.get('/machine', headers=headers)
    assert response.status_code == 200
    for k in test_machine:
        assert k in response.json[0]
        if k != 'status':
            assert test_machine[k] == response.json[0][k]
    #assert response.json[0] == test_machine

@pytest.mark.parametrize('param',({'machines':'foo'},{'machineStatus':'broken'},{'machineStatus':15}))
def test_machine_get_inv_params(client, login, param):
    headers = {'Authorization':login}
    headers.update(param)
    response = client.get('/machine', headers=headers)
    assert response.status_code == 400

def test_machine_get_not_auth(client, login, ):
    headers = {'machines':'1'}
    response = client.get('/machine', headers=headers)
    assert response.status_code == 401

def test_machine_id_get(client, login, test_machine):
    headers = {'Authorization':login}
    response = requests.get('https://localhost/machine/'+str(test_machine['id']), headers=headers, verify=False)
    #response = client.get('/machine/1', headers=headers)
    assert response.status_code == 200
    for k in test_machine:
        assert k in response.json()[0]
        if k != 'status':
            assert test_machine[k] == response.json()[0][k]
    #assert response.json()[0] == test_machine

def test_machine_id_get_not_found(client, login, ):
    headers = {'Authorization':login}
    response = requests.get('https://localhost/machine/9999', headers=headers, verify=False)
    #response = client.get('/machine/9999', headers=headers)
    assert response.status_code == 404

def test_machine_id_kpi_get_list(client, login, test_machine):
    headers = {'Authorization':login}
    response = requests.get('https://localhost/machine/'+str(test_machine['id'])+'/KPIList', headers=headers, verify=False)
    #response = client.get('/machine/1', headers=headers)    
    assert response.status_code == 200
    assert len(response.json()[0])

def test_machine_id_kpi_get_list_not_found(client, login, ):
    headers = {'Authorization':login}
    response = requests.get('https://localhost/machine/9999/KPIList', headers=headers, verify=False)
    #response = client.get('/machine/1', headers=headers)    
    assert response.status_code == 404

def test_machine_status_get(client, login, test_machine):
    headers = {'machines':str(test_machine['id']),'Authorization':login}
    response = client.get('/machine/status', headers=headers)
    assert response.status_code == 200
    assert (response.json[0]['status'] == 'operational') or (response.json[0]['status'] == 'idle') # Depends on the order of the other tests...

def test_machine_status_get_inv_params(client, login, ):
    headers = {'machines':'foo','Authorization':login}
    response = client.get('/machine/status', headers=headers)
    assert response.status_code == 400

def test_machine_summary_get(client, login, test_machine):
    headers = {'machines':str(test_machine['id']),'Authorization':login}
    response = client.get('/machine/summary', headers=headers)
    assert response.status_code == 200
    for k in response.json[0]:
        assert k in test_machine
        assert response.json[0][k] == test_machine[k]

@pytest.mark.parametrize('param',({'machines':'foo'},{'productionLines':'first,second'}))
def test_machine_summary_get_inv_params(client, login, param):
    headers = {'Authorization':login}
    headers.update(param)
    response = client.get('/machine/summary', headers=headers)
    assert response.status_code == 400

@pytest.mark.order(-3)
def test_machine_id_put(client, login, test_machine):
    headers = {'Authorization':login, 'name':'testPut'}
    response = requests.put('https://localhost/machine/'+str(test_machine['id']), headers=headers, verify=False)
    assert response.status_code == 200
    headers = {'Authorization':login, 'machines':str(test_machine['id'])}
    response = client.get('/machine', headers=headers)
    assert response.json[0]['name'] == 'testPut'

@pytest.mark.order(-2)
def test_machine_delete(client, login, test_machine):
    machine_id = test_machine['id']
    headers = {'Authorization':login, 'id': str(machine_id)}
    #response = client.delete('/machine/'+machine_id, headers=headers)
    response = requests.delete('https://localhost/machine/'+str(machine_id), headers=headers, verify=False)
    assert response.status_code == 200

@pytest.mark.order(-1)
def test_machine_delete_not_found(client, login, test_machine):
    machine_id = test_machine['id']
    headers = {'Authorization':login, 'id': str(machine_id)}
    #response = client.delete('/machine/'+machine_id, headers=headers)
    response = requests.delete('https://localhost/machine/'+str(machine_id), headers=headers, verify=False)
    assert response.status_code == 404