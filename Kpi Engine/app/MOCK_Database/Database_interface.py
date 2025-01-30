#from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import os
import sys
import pprint
import os
from os import path

s = os.path.abspath(os.path.join(os.path.dirname(__file__)))



import requests




def GetTimeRange(start_time, end_time):
    return np.array([i for i in set(Dataset[(Dataset["time"] >= start_time) & (Dataset["time"] <= end_time)]["time"])])
def GetValues(machine, KPI, range, operation = "sum"):
    Dataset = pd.read_csv(path.join("MOCK_Database", "smart_app_data.csv"))
    id_conv=list(set(Dataset["asset_id"]))
    return Dataset[(Dataset["asset_id"] == id_conv[machine]) &
                    (Dataset["kpi"] == KPI) &
                    (Dataset["time"] >= range[0]) &
                    (Dataset["time"] <= range[1])][operation].to_numpy()

BASE_URL='https://api-layer'

AUTH_URL = f'{BASE_URL}/user/login'

YOUR_USERNAME='admin'
YOUR_PASSWORD='admin'

auth_token = None

def get_token(url, username, password):
    headers = {
        'username': username,
        'password': password
    }  
    response = requests.post(url, headers=headers, verify=False)
    if response.status_code == 200:
        print('You are authenticated!')
        return response.json()
    elif response.status_code == 400:
        print('Wrong credentials')
    elif response.status_code == 500:
        print('Connection error')
    else:
        print('Unknown error')
    return None

auth_token = get_token(AUTH_URL, YOUR_USERNAME, YOUR_PASSWORD)

def call_with_token(url, token, call_type='GET', header_params=None):
    headers = {} if header_params is None else header_params
    headers['Authorization'] = token
    if call_type == 'GET':
        response = requests.get(url, headers=headers, verify=False)
    elif call_type == 'POST':
        response = requests.post(url, headers=headers, verify=False)
    elif call_type == 'PUT':
        response = requests.put(url, headers=headers, verify=False)
    elif call_type == 'DELETE':
        response = requests.delete(url, headers=headers, verify=False)
    else:
        print('Unknown call type')
        return None, None
    if response.status_code == 500:
        print('Server error: ', response.reason)
        return None, response.status_code
    elif response.status_code == 400:
        print('Bad request: ', response.reason)
        return None, response.status_code
    elif response.status_code == 401:
        print('Unauthorized')
        return None, response.status_code
    elif response.status_code == 200:
        return response.json(), response.status_code
    else:
        print('Unknown error: ', response.reason)
        return None, response.status_code

def call_and_retry(url, token, call_type='GET', header_params=None):
    response, status = call_with_token(url, token, call_type, header_params)
    if status == 401:
        print('Token expired, getting new token')
        token = get_token(AUTH_URL, YOUR_USERNAME, YOUR_PASSWORD)
        if token is None:
            print('Failed to get new token')
            return None, 401
        return call_and_retry(url, token, call_type, header_params)
    return response, status

def retrieve_data_db(machine:int, KPIs:list, aggregation_operation:str,range:tuple):
    DB_URL=f'{BASE_URL}/data/raw'
    token=get_token(AUTH_URL,YOUR_USERNAME,YOUR_PASSWORD)

    #start_time,end_time=range


    machine_kpis,code_status=call_and_retry(DB_URL,token,header_params={
        'machine_id':str(machine),
        'dataTypes': ','.join(KPIs),
        'aggregationOperation':aggregation_operation,
        #'from':start_time,
        #'to':end_time,
        'aggregationSelector':'sum'
    })
    if machine_kpis is None: 
        return None
    pprint(machine_kpis)
    result=dict()
    for kpi_data in machine_kpis:
        result[ kpi_data['KPI'] ]=kpi_data['valueSeries']

    return result

class DBConnection:

    def retrieve_data_db(machine:int, KPIs:list, aggregation_operation:str,range:tuple):
        DB_URL=f'{BASE_URL}/data/raw'
        token=get_token(AUTH_URL,YOUR_USERNAME,YOUR_PASSWORD)
        start_time,end_time=range

        machine_kpis,code_status=call_and_retry(DB_URL,token,header_params={
            'machines':str(machine),
            'dataTypes': ','.join(KPIs),
            'aggregationSelector':aggregation_operation,
            'from':start_time,
            'to':end_time,
        })

        if machine_kpis is None or len(machine_kpis)==0:
            return {kpi:np.array([]) for kpi in KPIs}, []
        result=dict()
        
        time_data=machine_kpis[0]['timestampSeries'] if (not machine_kpis[0]['timestampSeries'] is None)  else []

        for kpi_data in machine_kpis:
            result[ kpi_data['KPI'] ]=np.array(kpi_data['valueSeries'])
        return result,time_data
    
    def get_time_range(time_range,start_time, end_time):
        # Define the time range
        start_time = datetime.strptime(start_time,"%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end_time,"%Y-%m-%d %H:%M:%S")
        time_range=list(map(lambda x: datetime.strptime(x,"%Y-%m-%d %H:%M:%S") ,time_range))
        # Filter strings within the time range
        filtered_times = [
            timestamp_point for timestamp_point in time_range
            if start_time <= timestamp_point <= end_time
        ]
        return np.array(
            list(
                set(
                    filtered_times
                )
            )
        )
        #return np.array([i for i in set(Dataset[(Dataset["time"] >= start_time) & (Dataset["time"] <= end_time)]["time"])])