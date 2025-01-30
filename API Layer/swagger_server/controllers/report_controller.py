"""
    This module contains methods that handle REST API requests related to reports.
"""
import connexion
import six

from swagger_server.models.id import ID  # noqa: E501
from swagger_server.models.report import Report  # noqa: E501
from swagger_server.models.report_header import ReportHeader  # noqa: E501
from swagger_server import util



def report_get(start_time=None, end_time=None):  # noqa: E501
    """[Unimplemented] Returns list of reports

    Returns a list of reports. Optionally filtered over a given time period. By default, all the reports are returned # noqa: E501

    :param start_time: Starting time of the reports
    :type start_time: str
    :param end_time: Ending time of the reports
    :type end_time: str

    :rtype: List[ReportHeader]
    """
    # unimplemented
    return 'Unimplemented', 501


def report_id_get(id):  # noqa: E501
    """[Unimplemented] Returnsreport data

    Returns a report given its id # noqa: E501

    :param id: ID of the resource
    :type id: dict | bytes

    :rtype: List[Report]
    """
    # unimplemented
    return 'Unimplemented', 501