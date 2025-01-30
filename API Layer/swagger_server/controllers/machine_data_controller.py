"""
    This module contains methods that handle REST API requests related to machines.
"""
import connexion
import six

from swagger_server.models.id import ID  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.kpiid import KPIID  # noqa: E501
from swagger_server.models.machine_basic_info import MachineBasicInfo  # noqa: E501
from swagger_server.models.machine_complete_info import MachineCompleteInfo  # noqa: E501
from swagger_server.models.machine_id_filter import MachineIDFilter  # noqa: E501
from swagger_server.models.machine_not_found_error import MachineNotFoundError  # noqa: E501
from swagger_server.models.machine_status import MachineStatus  # noqa: E501
from swagger_server import util

from swagger_server.utils import connection_utils
from swagger_server.utils.header_parameters import ParameterFormatter
from swagger_server.utils import db_retrieval


def machine_delete(id_):  # noqa: E501
    """Deletes machine informations

    Deletes informations of a given machine # noqa: E501

    :param id: ID of the resource
    :type id: dict | bytes

    :rtype: str
    """

    # Execute postgreSQL stored procedure using arguments
    res, status_code = db_retrieval.delete_machine(id_)
    return res, status_code


def machine_get():  # noqa: E501
    """Gets machine related informations

    Returns machine informations including status according to optional filters. The query can be restricted over machine ids, machine types, production lines, factories and machine status. A non specified parameter implies no selection will be performed over it. For efficiency purposes, if status data is not required, refer to /machine/summary instead. # noqa: E501

    :param machines: Specific machines to restrict the query to
    :type machines: dict | bytes
    :param machine_types: Specific machine types to restrict the query to
    :type machine_types: List[str]
    :param production_lines: Specific production lines to restrict the query to
    :type production_lines: List[int]
    :param factories: Specific factories to restrict the query to
    :type factories: List[str]
    :param machine_status: Specific machine status to restrict the query to
    :type machine_status: dict | bytes

    :rtype: List[MachineCompleteInfo]
    """

    # Parse parameters
    machines = None
    machine_types = None
    production_lines = None
    factories = None
    machine_status = None
    try:
        machines = ParameterFormatter(connexion.request, 'machines').as_list_of_int()
        machine_types = ParameterFormatter(connexion.request, 'machinetypes').as_list_of_string()
        production_lines = ParameterFormatter(connexion.request, 'productionlines').as_list_of_int()
        factories = ParameterFormatter(connexion.request, 'factories').as_list_of_string()
        machine_status = ParameterFormatter(connexion.request, 'machinestatus').as_string()
    except Exception as e:
        return 'Invalid parameters', 400
    # enum check
    if machine_status is not None:
        if machine_status not in ['operational', 'idle']:
            return 'Invalid machineStatus', 400

    if machine_status is not None:
        machine_status = True if machine_status == 'operational' else False

    # Execute postgreSQL stored procedure using arguments
    res, status_code = db_retrieval.get_machine_info_with_status(machines, machine_types, production_lines, factories, machine_status)
    return res, status_code

def machine_id_get(id_):  # noqa: E501
    """Returns informations of a given machine

    Returns all informations of a machine given its id(including machine status, see /machine/status for details). # noqa: E501

    :param id: ID of the resource
    :type id: dict | bytes

    :rtype: MachineCompleteInfo
    """

    # Execute postgreSQL stored procedure using arguments
    res, status_code = db_retrieval.get_machine_info_with_status(machines=[id_])
    if status_code != 200:
        return res, status_code
    # check if the machine exists
    if len(res) == 0:
        return 'Machine not found', 404
    return res, status_code


def machine_id_kpi_list_get(id_):  # noqa: E501
    """Returns machine KPI list

    Returns the list of KPI supported by the machine according to its type. A KPI is considered as supported if the machine directly produces it or every KPI needed for its computation are supported by the machine. # noqa: E501

    :param id: ID of the resource
    :type id: dict | bytes

    :rtype: List[KPIID]
    """
    
    # Execute postgreSQL stored procedure using arguments
    res, status_code = db_retrieval.get_kpi_list_from_machine_id(id_)
    return res, status_code


def machine_id_put(id_):  # noqa: E501
    """Updates machine data

    Modifies the name, production line, factory and/or machine type of a given machine. If a parameter is not provided, the original machine data for it will be kept # noqa: E501

    :param id: ID of the resource
    :type id: dict | bytes
    :param name: The updated name of the machine
    :type name: str
    :param production_line: The updated production line of the machine
    :type production_line: int
    :param factory: The updated factory of the machine
    :type factory: str
    :param machine_type: The updated machine type of the machine
    :type machine_type: str

    :rtype: str
    """

    # check if the machine exists
    res, status_code = db_retrieval.get_machine_info(machines=[id_])
    if len(res) == 0:
        return 'Machine not found', 404

    # Parse parameters
    name = None
    production_line = None
    factory = None
    machine_type = None
    try:
        name = ParameterFormatter(connexion.request, 'name').as_string()
        production_line = ParameterFormatter(connexion.request, 'productionline').as_string()
        factory = ParameterFormatter(connexion.request, 'factory').as_string()
        machine_type = ParameterFormatter(connexion.request, 'machinetype').as_string()
    except Exception as e:
        return 'Invalid parameters', 400

    # Execute postgreSQL stored procedure using arguments
    res, status_code = db_retrieval.update_machine(id_, name, production_line, factory, machine_type)
    return res, status_code


def machine_post():  # noqa: E501
    """Adds a new machine to the system

    Adds a new machine to the system by providing its informations. The created machine id will be returned in case of a successful request. # noqa: E501

    :param name: The name of the machine
    :type name: str
    :param production_line: The production line of the machine
    :type production_line: int
    :param factory: The factory of the machine
    :type factory: str
    :param machine_type: The machine type of the machine
    :type machine_type: str

    :rtype: ID
    """

    # Parse parameters
    name = None
    production_line = None
    factory = None
    machine_type = None
    try:
        name = ParameterFormatter(connexion.request, 'name').as_string()
        production_line = ParameterFormatter(connexion.request, 'productionline').as_string()
        factory = ParameterFormatter(connexion.request, 'factory').as_string()
        machine_type = ParameterFormatter(connexion.request, 'machinetype').as_string()
    except Exception as e:
        return 'Invalid parameters', 400
    
    # Execute postgreSQL stored procedure using arguments
    res, status_code = db_retrieval.add_machine(name, production_line, factory, machine_type)
    return res, status_code

def machine_status_get(machines=None):  # noqa: E501
    """Gets status informations of machines

    Returns the status of all machines unless a list of machine ids is provided as filter, in which case only the requested machines status will be returned. The status of a machine indicates whether sensor data for it has not been collected for 30 hours. # noqa: E501

    :param machines: Specific machines to restrict the query to
    :type machines: dict | bytes

    :rtype: List[InlineResponse200]
    """

    # Parse parameters
    machines = None
    try:
        machines = ParameterFormatter(connexion.request, 'machines').as_list_of_int()
    except Exception as e:
        return 'Invalid parameters', 400

    # Execute postgreSQL stored procedure using arguments
    res, status_code = db_retrieval.get_machine_status(machines=machines)
    return res, status_code


def machine_summary_get(machines=None, machine_types=None, production_lines=None, factories=None):  # noqa: E501
    """Gets basic machine informations

    Returns machine informations according to optional filters. The query can be restricted over machine ids, machine types, production lines and factories. A non specified parameter implies no selection will be performed over it. # noqa: E501

    :param machines: Specific machines to restrict the query to
    :type machines: dict | bytes
    :param machine_types: Specific machine types to restrict the query to
    :type machine_types: List[str]
    :param production_lines: Specific production lines to restrict the query to
    :type production_lines: List[int]
    :param factories: Specific factories to restrict the query to
    :type factories: List[str]

    :rtype: List[MachineBasicInfo]
    """

    # Parse parameters
    machines = None
    machine_types = None
    production_lines = None
    factories = None
    try:
        machines = ParameterFormatter(connexion.request, 'machines').as_list_of_int()
        machine_types = ParameterFormatter(connexion.request, 'machinetypes').as_list_of_string()
        production_lines = ParameterFormatter(connexion.request, 'productionlines').as_list_of_int()
        factories = ParameterFormatter(connexion.request, 'factories').as_list_of_string()
    except Exception as e:
        return 'Invalid parameters', 400

    # Execute postgreSQL stored procedure using arguments
    res, status_code = db_retrieval.get_machine_info(machines, machine_types, production_lines, factories)
    return res, status_code