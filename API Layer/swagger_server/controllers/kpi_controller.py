"""
    This module contains methods that handle REST API requests related to KPIs.
"""
import connexion
import six
import requests
import json

from swagger_server.models.aggregation_type import AggregationType  # noqa: E501
from swagger_server.models.id import ID  # noqa: E501
from swagger_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from swagger_server.models.inline_response404 import InlineResponse404  # noqa: E501
from swagger_server.models.kpi_basic_info import KPIBasicInfo  # noqa: E501
from swagger_server.models.kpiid import KPIID  # noqa: E501
from swagger_server.models.kpi_not_found_error import KPINotFoundError  # noqa: E501
from swagger_server.models.machine_kpi_values import MachineKPIValues  # noqa: E501
from swagger_server import util
from swagger_server.utils.header_parameters import ParameterFormatter
from swagger_server.utils import db_retrieval
from datetime import datetime

KPISERVICE = 'kpi-engine'
PORT = '8000'
KPIURL = 'http://'+KPISERVICE+':'+PORT
TIMEOUT = 60

def kpi_get():  # noqa: E501
    """Returns all supported KPI

    Returns the set of all KPI supported by the machines(directly produced or computed by the KPI engine), optionally filtered by KPI id and category. If the formula of a KPI is null, it is a basic KPI, otherwise can be computed by the KPI engine. # noqa: E501

    :param kpi_filter: Optional list of KPI ids to restrict the query to
    :type kpi_filter: List[str]
    :param category_filter: Optional list of KPI categories to restrict the query to
    :type category_filter: List[str]

    :rtype: List[KPIBasicInfo]
    """
    # Parse parameters
    kpi_filter = None
    category_filter = None
    try:
        kpi_filter = ParameterFormatter(connexion.request, 'kpiFilter').as_list_of_string()
        category_filter = ParameterFormatter(connexion.request, 'categoryFilter').as_list_of_string()
    except Exception as e:
        return 'Invalid parameters', 400
    
    res, status_code = db_retrieval.get_kpi_list(kpi_filter, category_filter)
    return res, status_code
    

def kpi_id_get(kpiid):  # noqa: E501
    """Get basic informations on a given KPI

    Returns basic informations on a KPI given its name. A null formula implies it is a basic KPI. # noqa: E501

    :param kpiid: ID of the KPI
    :type kpiid: dict | bytes

    :rtype: KPIBasicInfo
    """
    res, status_code = db_retrieval.get_kpi_list([kpiid], None)
    if status_code != 200:
        return res, status_code
    if len(res) == 0:
        return 'KPI not found', 404
    return res, status_code


def kpi_id_machine_kpi_values_get(kpiid, machine_id):  # noqa: E501
    """Returns a series of KPI values of a machine

    Returns a series of KPI values of a machine. A timeframe can be provided to only retrieve KPI data in the interval [start, end). This timeframe will be divided in intervals according to &#x27;aggregationInterval&#x27; parameter. On each interval the function &#x27;aggregationOp&#x27; will be applied, returning one item per interval. Checks will be performed to ensure the machine and KPI exist (in case they don&#x27;t a 404 error will be returned) and the machine supports the KPI(in case this is false a 400 error will be returned). # noqa: E501

    :param kpiid: ID of the KPI
    :type kpiid: dict | bytes
    :param machine_id: ID of the machine
    :type machine_id: int
    :param start_date: The first timestamp of the time window of results
    :type start_date: str
    :param end_date: The last timestamp of the time window of results
    :type end_date: str
    :param aggregation_op: Aggregation function to perform (defaults to sum)
    :type aggregation_op: dict | bytes
    :param aggregation_interval: Requested time granularity of KPI (defaults to day)
    :type aggregation_interval: str

    :rtype: MachineKPIValues
    """
    # Parse parameters
    start_date = None
    end_date = None
    aggregation_op = None
    aggregation_interval = None
    try:
        start_date = ParameterFormatter(connexion.request, 'startDate').as_datetime_from_date()
        end_date = ParameterFormatter(connexion.request, 'endDate').as_datetime_from_date()
        aggregation_op = ParameterFormatter(connexion.request, 'aggregationOp').as_string()
        aggregation_interval = ParameterFormatter(connexion.request, 'aggregationInterval').as_string()
    except Exception as e:
        return 'Invalid parameters', 400
    
    # enum check
    if aggregation_op is not None:
        if aggregation_op not in ['avg', 'min', 'max', 'sum']:
            return 'Invalid aggregationOp', 400
    else:
        aggregation_op = 'sum'

    if aggregation_interval is not None:
        if aggregation_interval not in ['day', 'week', 'month', 'year', 'overall']:
            return 'Invalid aggregationInterval', 400
    else:
        aggregation_interval = 'day'

    # Python 3.8 does not support match construct...
    if aggregation_interval == 'day': aggregation_interval = 'd'
    elif aggregation_interval == 'week': aggregation_interval = 'w'
    elif aggregation_interval == 'month': aggregation_interval = 'm'
    elif aggregation_interval == 'year': aggregation_interval = 'y'
    else: aggregation_interval = '-' # overall

    # check if machine and kpi exist, check if machine supports kpi
    res, status_code = db_retrieval.allowed_kpi_machine(machine_id, kpiid)
    if status_code != 200:
        return res, status_code
    if not res:
        return 'Machine does not support KPI', 400

    expression = f'{aggregation_op}({kpiid})'
    start_date = datetime.strftime(start_date, "%Y-%m-%d") if start_date is not None else None
    end_date = datetime.strftime(end_date, "%Y-%m-%d") if end_date is not None else None
    pars = {'machine_id': machine_id, 'start_date': start_date, 'end_date': end_date, 'expression': expression,'unit':aggregation_interval, 'operation':aggregation_op}
    try:
        response = requests.get(KPIURL+'/calculate/', params=pars, timeout=TIMEOUT, verify=False)
        if response.status_code != 200:
            error_message = response.json()['reason']
            return f"KPI engine error: {error_message}", response.status_code
        response = response.json()
        if response['code'] != 0:
            return response['reason'], 400
        res = response['result']
        final_series = []
        for el in res:
            start_date = el['start_time'].split(' ')[0]
            end_date = el['end_time'].split(' ')[0]
            # check for nan values
            if el['values'] != "nan val":
                final_series.append({'startDate': start_date, 'endDate': end_date, 'value': el['values']})
        final_res_dict = {'unit': response['unit'], 'values': final_series}
        return final_res_dict, 200
    except Exception as e:
        print(e, flush=True)
        return 'KPI engine error', 500


def kpi_id_machines_get(kpiid):  # noqa: E501
    """Returns machines that support KPI

    Returns the set of all machine ids supporting the KPI. A KPI is considered as supported if the machine directly produces it or every KPI needed for its computation are supported by the machine. # noqa: E501

    :param kpiid: ID of the KPI
    :type kpiid: dict | bytes

    :rtype: InlineResponse2001
    """
    
    res, status_code = db_retrieval.get_machines_by_kpi(kpiid)
    return res, status_code


def kpi_post(body):  # noqa: E501
    """[Unimplemented] Adds a new KPI to the system

     # noqa: E501

    :param body: Required KPI object to post
    :type body: dict | bytes

    :rtype: ID
    """
    # unimplemented
    return 'Unimplemented', 501
