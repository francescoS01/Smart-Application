# coding: utf-8
"""
    Tests related to alert endpoints
"""

import pytest
import requests

@pytest.fixture(scope='session')
def alert():
    a = {
        'alertDescription':'Test',
        'kpi':'good_cycles',
        'severity':'medium',
        'timestamp':'2000-01-01 00:00:00',
    }
    return a

@pytest.fixture(scope='session')
def monitor():
    m = {
         'timeWindow':3600.00,
         'expression':'avg(bad_cycles)>10'
    }
    return m

@pytest.mark.order("first", after="test_machine_data_controller.py::test_machine_post", before="test_machine_data_controller.py::test_machine_delete")
def test_alert_post(client, login, alert, test_machine):
    alert['machineID'] = test_machine['id']
    headers = {'Authorization': login, 'machineID':str(test_machine['id']), 'description':'Test', 
               'KPI':'good_cycles', 'severity':'medium', 'timestamp':'2000-01-01 00:00:00'}
    response = client.post('/alert', headers=headers)
    assert response.status_code == 201
    alert['id'] = response.json

@pytest.mark.order(after="test_alert_post", before="test_machine_data_controller.py::test_machine_delete")
def test_alert_get(client, login, alert):
    headers = {'Authorization':login,'machines':str(alert['machineID'])}
    response = client.get('/alert', headers=headers)
    assert response.status_code == 200
    assert response.json[0] == alert, response.json
    
@pytest.mark.parametrize('param',({'machines':'foo'},{'severity':'0'},{'from':'15'}))
def test_alert_get_inv_params(client, login, param):
    headers = {'Authorization':login}
    headers.update(param)
    response = client.get('/alert', headers=headers)
    assert response.status_code == 400

def test_alert_get_not_auth(client, login):
    response = client.get('/alert')
    assert response.status_code == 401

@pytest.mark.order(after="test_alert_post", before="test_machine_data_controller.py::test_machine_delete")
def test_alert_id_get(client, login, alert):
    headers = {'Authorization':login}
    response = requests.get('https://localhost/alert/id/'+str(alert['id']), headers=headers, verify=False)
    #response = client.get('/alert/id/1', headers=headers)    
    assert response.status_code == 200
    assert response.json()[0] == alert

def test_alert_id_get_not_found(client, login, alert):
    headers = {'Authorization':login}
    response = requests.get('https://localhost/alert/id/9999', headers=headers, verify=False)
    #response = client.get('/alert/id/9999', headers=headers)    
    assert response.status_code == 404

@pytest.mark.order(after="test_alert_post", before="test_machine_data_controller.py::test_machine_delete")
def test_alert_machine_id(client, login, alert):
    headers = {'Authorization':login}
    response = requests.get('https://localhost/alert/machine/'+str(alert['machineID']), headers=headers, verify=False)
    #response = client.get('/alert/machine/1', headers=headers)
    assert response.status_code == 200
    assert response.json()[0] == alert

@pytest.mark.parametrize('param',({'startTime':'15'},{'endTime':'tomorrow'}))
def test_alert_machine_id_inv_params(client, login, param, alert):
    headers = {'Authorization':login}
    headers.update(param)
    response = requests.get('https://localhost/alert/machine/'+str(alert['machineID']), headers=headers, verify=False)
    #response = client.get('/alert/machine/1', headers=headers)
    assert response.status_code == 400

@pytest.mark.order(after="test_machine_data_controller.py::test_machine_post", before="test_machine_data_controller.py::test_machine_delete")
def test_alert_monitor_post(client, login, monitor, test_machine):
    monitor['machineID'] = test_machine['id']
    headers = {'Authorization':login,'machineID':str(test_machine['id']), 'timeWindow':3600, 'expression':'avg(bad_cycles)>10'}
    response = client.post('/alert/monitor', headers=headers)
    assert response.status_code == 201
    monitor['monitorUUID'] = response.json

@pytest.mark.order(after="test_alert_monitor_post")
def test_alert_monitor_get(client, login, monitor):
    headers = {'Authorization':login}
    response = client.get('/alert/monitor', headers=headers)
    assert response.status_code == 200
    assert len(list(filter(lambda m: m['monitorUUID'] == monitor['monitorUUID'], response.json))) > 0

@pytest.mark.order(after="test_alert_monitor_get")
def test_alert_monitor_delete(client, login, monitor):
    headers = {'Authorization':login}
    response = requests.delete('https://localhost/alert/monitor/'+str(monitor['monitorUUID']), headers=headers, verify=False)
    assert response.status_code == 200
    response = client.get('/alert/monitor', headers=headers)
    assert response.status_code == 200
    assert monitor not in response.json