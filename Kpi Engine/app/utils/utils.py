import re
import requests
from models import calculation_request
from datetime import datetime, timedelta
import pandas as pd
import math
import numpy as np
import itertools as it
def calculate_segments(
        start_date: datetime,
        end_date: datetime,
        unit: calculation_request.Units
    ):
    """
    calculate the time-segments ues to evalute the expressions from the kpi engine

    Args:
        start_date: initial time 
        start_date: final time 
        unit: the time-segments granularity
    
    Returns:
        a list of time-segments

    """
    time_range=pd.date_range(start_date, end_date)

    if unit == calculation_request.Units.NONE:
        time_range={
            f"{start_date}/{end_date}":[
                                            pd.Timestamp(start_date),
                                            pd.Timestamp(end_date)
                                        ]
        }

    elif unit == calculation_request.Units.DAY:
        # for days you have to specify the date or you get empty time-segments
        time_range=pd.date_range(start_date,end_date,freq='D')[:-1]
        tmp_res=dict()
        for d in time_range:
            tmp_res[d]=[
                d,
                d+timedelta(days=1)
            ]
        time_range=tmp_res
    elif unit == calculation_request.Units.WEEK:
        time_range=pd.date_range(start_date,end_date,freq='W')
        print(time_range)
        tmp_res=dict()
        for d,c in enumerate(it.pairwise(time_range)):
            tmp_res[d]=list(c)
        time_range=tmp_res
        print("WEEKLY",time_range)

    elif unit == calculation_request.Units.MONTH:
        time_range=pd.date_range(start_date,end_date,freq='M')
        tmp_res=dict()
        for d,c in enumerate(it.pairwise(time_range)):
            tmp_res[d]=list(c)
        time_range=tmp_res
    elif unit == calculation_request.Units.YEAR:
        time_range=pd.date_range(start_date,end_date,freq='Y')
        tmp_res=dict()
        for d,c in enumerate(it.pairwise(time_range)):
            tmp_res[d]=list(c)
        time_range=tmp_res
    return time_range

def remove_nan(x):
    """
    fix to long floats and remove nan values
    """
    return round(x,16) if not math.isnan(x) and not math.isinf(x) else "nan val"


def extract_kpi_names(expression,KB_kpis):
    """
    extract the given kpi names from the expresion
    """
    targets = KB_kpis
    # Create a single regex pattern for all targets
    pattern = r"|".join(fr"(?<!_)({re.escape(target)})(?!_)" for target in targets)

    # Find all matches
    matches = re.findall(pattern, expression)

    # Flatten the result (re.findall returns tuples when there are groups)
    matches = [match for match_group in matches for match in match_group if match]
    return matches

BASE_URL='https://api-layer'

AUTH_URL = f'{BASE_URL}/user/login'

YOUR_USERNAME='KPIENGINE'
YOUR_PASSWORD='password4'

def get_token(url, username, password):
    headers = {
        'username': username,
        'password': password
    }  
    response = requests.post(url, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()
    return None

#auth_token = get_token(AUTH_URL, YOUR_USERNAME, YOUR_PASSWORD)

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
        return None, None
    if response.status_code == 500:
        return None, response.status_code
    elif response.status_code == 400:
        return None, response.status_code
    elif response.status_code == 401:
        return None, response.status_code
    elif response.status_code == 200:
        return response.json(), response.status_code
    else:
        return None, response.status_code

def call_and_retry(url, token = None, call_type='GET', header_params=None):
    response, status = call_with_token(url, token, call_type, header_params)
    if status == 401:
        token = get_token(AUTH_URL, YOUR_USERNAME, YOUR_PASSWORD)
        if token is None:
            return None, 401
        return call_and_retry(url, token, call_type, header_params)
    return response, status