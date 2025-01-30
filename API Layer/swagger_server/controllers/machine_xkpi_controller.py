"""
    This module contains methods that handle REST API requests related to the relation between machines and KPIs.
"""
import connexion
import six

from swagger_server.models.machine_xkpi_info import MachineXKPIInfo  # noqa: E501
from swagger_server import util
from swagger_server.utils.header_parameters import ParameterFormatter
from swagger_server.utils import db_retrieval


def machine_xkpi_get():  # noqa: E501
    """Returns info on the relation between machines and KPIs

    Returns basic info on both machines and KPIs and the relation between them expressed as &lt;machine id, KPI numerical id&gt; pairs. # noqa: E501


    :rtype: MachineXKPIInfo
    """
    
    res, status = db_retrieval.get_machine_xkpi_info()
    return res, status
