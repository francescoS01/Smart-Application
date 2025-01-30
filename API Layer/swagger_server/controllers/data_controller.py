"""
    This module contains methods that handle REST API requests related to sensor data.
"""
import connexion
import six

from swagger_server.models.data_type_filter import DataTypeFilter  # noqa: E501
from swagger_server.models.inline_response404 import InlineResponse404  # noqa: E501
from swagger_server.models.kpiid import KPIID  # noqa: E501
from swagger_server.models.machine_id_filter import MachineIDFilter  # noqa: E501
from swagger_server.models.sensor_data import SensorData  # noqa: E501
from swagger_server import util
from swagger_server.utils.connection_utils import DBConnection
from swagger_server.utils.header_parameters import ParameterFormatter
from swagger_server.utils import db_retrieval


def data_get():  # noqa: E501
    """Gets raw sensors data filtered by machine ID, data type (as KPI ids), and time window

    Access to basic KPI related to sensor data. The query can be restricted to specific machines and/or KPIs given their ids and a time window. The time window is interpreted as [from, to). Since KPIs are aggregated using multiple functions, &#x27;aggregation selector&#x27; determines the type of aggregation to retrieve. # noqa: E501

    :param aggregation_selector: Aggregation type to retrieve
    :type aggregation_selector: str
    :param machines: Specific machines to restrict the query to
    :type machines: dict | bytes
    :param data_types: Specific basic kpi to restrict the query to
    :type data_types: dict | bytes
    :param _from: The first timestamp of the time window of results
    :type _from: str
    :param to: The last timestamp of the time window of results
    :type to: str

    :rtype: List[SensorData]
    """

    # Parse parameters
    _from = None
    to = None
    machines = None
    data_types = None
    aggregationType = None
    try:
        _from = ParameterFormatter(connexion.request, 'from').as_datetime()
        to = ParameterFormatter(connexion.request, 'to').as_datetime()
        machines = ParameterFormatter(connexion.request, 'machines').as_list_of_int()
        data_types = ParameterFormatter(connexion.request, 'dataTypes').as_list_of_string()
        aggregationType = ParameterFormatter(connexion.request, 'aggregationSelector').as_string()
    except Exception as e:
        return 'Invalid parameters', 400
    # enum check
    if aggregationType is not None:
        if aggregationType not in ['avg', 'min', 'max', 'sum']:
            return 'Invalid aggregationSelector', 400
    
    res, status_code = db_retrieval.get_sensor_data(machines, _from, to, data_types, aggregationType)
    return res, status_code

def data_preprocessed_get():  # noqa: E501
    """Gets preprocessed sensors data filtered by machine ID, data type (as KPI ids), and time window

    Access to basic KPI related to preprocessed sensor data. The query can be restricted to specific machines and/or KPIs given their ids and a time window. The time window is interpreted as [from, to). Since KPIs are aggregated using multiple functions, &#x27;aggregation selector&#x27; determines the type of aggregation to retrieve. # noqa: E501

    :param aggregation_selector: Aggregation type to retrieve
    :type aggregation_selector: str
    :param machines: Specific machines to restrict the query to
    :type machines: dict | bytes
    :param data_types: Specific basic kpi to restrict the query to
    :type data_types: dict | bytes
    :param _from: The first timestamp of the time window of results
    :type _from: str
    :param to: The last timestamp of the time window of results
    :type to: str

    :rtype: List[SensorData]
    """

    # Parse parameters
    _from = None
    to = None
    machines = None
    data_types = None
    aggregationType = None
    try:
        _from = ParameterFormatter(connexion.request, 'from').as_datetime()
        to = ParameterFormatter(connexion.request, 'to').as_datetime()
        machines = ParameterFormatter(connexion.request, 'machines').as_list_of_int()
        data_types = ParameterFormatter(connexion.request, 'dataTypes').as_list_of_string()
        aggregationType = ParameterFormatter(connexion.request, 'aggregationSelector').as_string()
    except Exception as e:
        return 'Invalid parameters', 400
    # enum check
    if aggregationType is not None:
        if aggregationType not in ['avg', 'min', 'max', 'sum']:
            return 'Invalid aggregationSelector', 400
        
    res, status_code = db_retrieval.get_preprocessed_data(machines, _from, to, data_types, aggregationType)
    return res, status_code

def data_post(machine_id, kpiid):  # noqa: E501
    """Adds new sensor data to the system

    Adds new aggregated values of a KPI for a given machine id. AggregationType and values must be of the same length. 400 error will be returned if the machine can&#x27;t generate such KPI. # noqa: E501

    :param kpiid: ID of the KPI
    :type kpiid: dict | bytes
    :param machine_id: ID of the machine
    :type machine_id: int
    :param aggregation_type: The aggregation types of the KPI values to be added
    :type aggregation_type: List[str]
    :param values: Aggregated values of the KPI
    :type values: List[float]

    :rtype: str
    """

    # Parse parameters
    aggregation_names = None
    values = None
    try:
        aggregation_names = ParameterFormatter(connexion.request, 'aggregationType').as_list_of_string()
        values = ParameterFormatter(connexion.request, 'values').as_list_of_float()
    except Exception as e:
        return 'Invalid parameters', 400
    # enum check
    if aggregation_names is not None:
        for aggregation_names_item in aggregation_names:
            if aggregation_names_item not in ['avg', 'min', 'max', 'sum']:
                return 'Invalid aggregationType', 400
    # check that the list of aggregation names and values are not empty
    if len(aggregation_names) == 0 or len(values) == 0:
        return 'Aggregation names and values must not be empty', 400
    # check that the length of the aggregation names and values are the same
    if len(aggregation_names) != len(values):
        return 'The length of the aggregation names and values must be the same', 400
    # check if the machine can generate the KPI
    request_res, request_status_code = db_retrieval.allowed_kpi_machine(machine_id, kpiid)
    if request_status_code != 200:
        return request_res, request_status_code
    if request_res == False:
        return 'The machine can\'t generate the KPI', 400

    res, status_code = db_retrieval.add_sensor_data_to_kafka(machine_id, kpiid, aggregation_names, values)
    return res, status_code