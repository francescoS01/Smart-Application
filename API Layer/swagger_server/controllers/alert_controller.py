"""
    This module contains methods that handle REST API requests related to alerts.
"""
import connexion
import six
import requests
import uuid

from swagger_server.models.alert import Alert  # noqa: E501
from swagger_server.models.alert_monitor import AlertMonitor  # noqa: E501
from swagger_server.models.id import ID  # noqa: E501
from swagger_server.models.kpiid import KPIID  # noqa: E501
from swagger_server.models.machine_id_filter import MachineIDFilter  # noqa: E501
from swagger_server.models.machine_not_found_error import MachineNotFoundError  # noqa: E501
from swagger_server.models.severity import Severity  # noqa: E501
from swagger_server import util

from swagger_server.utils import db_retrieval
from swagger_server.utils.header_parameters import ParameterFormatter


KPISERVICE = 'kpi-engine'
PORT = '8000'
KPIURL = 'http://'+KPISERVICE+':'+PORT
TIMEOUT = 60

def alert_get(machines=None, severity=None, _from=None, to=None):  # noqa: E501
    """Gets alerts fitered by machine ID, severity, and time window

    Returns informations related to alerts, optionally restricted to given machine ids, alert importance and time window. # noqa: E501

    :param machines: Specific machines to restrict the query to
    :type machines: dict | bytes
    :param severity: Alerts importance to restrict the query to.
    :type severity: dict | bytes
    :param _from: First timestamp of the time window of results
    :type _from: str
    :param to: Last timestamp of the time window of results
    :type to: str

    :rtype: List[Alert]
    """
    
    # Parse parameters
    try:
        machines = ParameterFormatter(connexion.request, 'machines').as_list_of_int()
        severity = ParameterFormatter(connexion.request, 'severity').as_string()
        _from = ParameterFormatter(connexion.request, 'from').as_datetime()
        to = ParameterFormatter(connexion.request, 'to').as_datetime()
    except:
        return 'Invalid parameters', 400
    
    if severity is not None:
        if severity == 'low':
            severity = 1
        elif severity == 'medium':
            severity = 2
        elif severity == 'high':
            severity = 3
        else:
            return 'Invalid parameters', 400

    # Execute postgreSQL stored procedure using arguments
    res, status_code = db_retrieval.get_alerts_filtered(machines, severity, _from, to)
    return res, status_code


def alert_id_get(id_):  # noqa: E501
    """Gets single alert by alert ID

    Gets informations on an alert given its id. # noqa: E501

    :param id: ID of the resource
    :type id: dict | bytes

    :rtype: Alert
    """

    # Execute postgreSQL stored procedure using arguments
    res, status_code = db_retrieval.get_alert_info(alert_id=[id_])
    # check if the machine exists
    if len(res) == 0:
        return 'Machine not found', 404
    return res, status_code


def alert_machine_id(id_, start_time=None, end_time=None):  # noqa: E501
    """Returns alerts of a given machine

    Returns a list of alerts of a given machine(identified by its id), optionally filtered over a given time period. By default, all the alerts of such machine are returned. # noqa: E501

    :param id: ID of the resource
    :type id: dict | bytes
    :param start_time: Starting time of the alerts
    :type start_time: str
    :param end_time: Ending time of the alerts
    :type end_time: str

    :rtype: List[Alert]
    """
    
    # Parse parameters
    try:
        start_time = ParameterFormatter(connexion.request, 'startTime').as_datetime()
        end_time = ParameterFormatter(connexion.request, 'endTime').as_datetime()
    except:
        return 'Invalid parameters', 400
    
    #check if the machine exists
    machine_name = db_retrieval.get_machine_name_by_id(machine_id=id_)
    if machine_name is None:
        return 'Machine not found', 404
    
    # Execute postgreSQL stored procedure using arguments
    res, status_code = db_retrieval.get_alerts_filtered(machines=[id_], start_time=start_time, end_time=end_time)    
    return res, status_code


def alert_monitor_get():  # noqa: E501
    """Returns the list of monitored KPI expressions

    Returns the list of KPI expressions monitored by the KPI engine to fire alerts. # noqa: E501


    :rtype: List[AlertMonitor]
    """
    
    response = requests.get(KPIURL+'/get_all_alerts/', timeout=TIMEOUT, verify=False)
    if response.status_code != 200:
        return 'KPI engine error', 500
    response = response.json()
    return response


def alert_monitor_id_delete(uuid):  # noqa: E501
    """Removes a monitored expression

    Removes a monitored expression given its id. # noqa: E501

    :param uuid: UUID of the resource
    :type uuid: dict | bytes

    :rtype: str
    """
    pars = {'alerts_ids': [uuid]}
    response = requests.delete(KPIURL+'/remove_alerts/', json=pars, timeout=TIMEOUT, verify=False)
    try:
        res = response.json()
        if not res[uuid]:
            return 'Alert monitor not found', 404
    except:
        return 'KPI engine error', 500
    return 'Alert monitor removed', 200

def alert_monitor_post():  # noqa: E501
    """Adds a new alert monitor

    Adds a new expression to the list of monitored expressions used to fire alerts. # noqa: E501

    :param time_window: Time in seconds used to evaluate the expression, a window of 3600 evaluates the expression on the last hour
    :type time_window: int
    :param expression: Expression involving KPIs and aggregation functions on a given machine
    :type expression: str
    :param machine_id: Id of the machine to monitor
    :type machine_id: dict | bytes

    :rtype: str
    """
    # Parse parameters
    time_window = None
    expression = None
    machine_id = None
    try:
        time_window = ParameterFormatter(connexion.request, 'timeWindow').as_float()
        expression = ParameterFormatter(connexion.request, 'expression').as_string()
        machine_id = ParameterFormatter(connexion.request, 'machineID').as_int()
    except:
        return 'Invalid parameters', 400
    if None in [time_window, expression, machine_id]:
        return 'Invalid parameters', 400
    data = {
        'sliding_window_seconds': time_window,
        'expression': expression,
        'machine_id': machine_id
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(KPIURL+'/add_alert/', json=data, headers=headers, timeout=TIMEOUT, verify=False)
    if response.status_code != 200:
        return 'KPI engine error', 500
    
    response = response.json()

    return response['newID'], 201


def alert_post():  # noqa: E501
    """Posts new alert

    Adds a new alert to the system. Checks for machine existence (404 if the machine doesn&#x27;t exist). Returns the id of the added alert if successful. # noqa: E501

    :param timestamp: Time of generation of the alert
    :type timestamp: str
    :param machine_id: ID of the machine related to the new alert
    :type machine_id: dict | bytes
    :param severity: Importance of the new alert
    :type severity: dict | bytes
    :param description: Description of the alert
    :type description: str
    :param kpi: ID of the KPI or an expression with KPI IDs related to the new alert
    :type kpi: dict | bytes

    :rtype: ID
    """
    # Parse parameters
    timestamp = None
    machine_id = None
    severity = None
    description = None
    kpi = None
    try:
        timestamp = ParameterFormatter(connexion.request, 'timestamp').as_datetime()
        machine_id = ParameterFormatter(connexion.request, 'machineid').as_int()
        severity = ParameterFormatter(connexion.request, 'severity').as_string()
        description = ParameterFormatter(connexion.request, 'description').as_string()
        kpi = ParameterFormatter(connexion.request, 'kpi').as_string()
    except:
        return 'Invalid parameters', 400
    
    if severity is not None:
        if severity == 'low':
            severity = 1
        elif severity == 'medium':
            severity = 2
        elif severity == 'high':
            severity = 3
        else:
            return 'Invalid parameters', 400
    # ensure all parameters are valid
    if None in [timestamp, machine_id, severity, description, kpi]:
        return 'Invalid parameters', 400
    # check if the machine exists
    machine_name = db_retrieval.get_machine_name_by_id(machine_id)
    if machine_name is None:
        return 'Machine not found', 404
    # Execute postgreSQL stored procedure using arguments
    res, status_code = db_retrieval.add_alert(machine_id, severity, description, timestamp, kpi)
    return res, status_code