"""
    Tests related to report endpoints
"""
# coding: utf-8


from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.id import ID  # noqa: E501
from swagger_server.models.report import Report  # noqa: E501
from swagger_server.models.report_header import ReportHeader  # noqa: E501
from swagger_server.test import BaseTestCase


class TestReportController(BaseTestCase):
    """ReportController integration test stubs"""

    def test_report_get(self):
        """Test case for report_get

        [Unimplemented] Returns list of reports
        """
        headers = [('start_time', '2013-10-20T19:20:30+01:00'),
                   ('end_time', '2013-10-20T19:20:30+01:00')]
        response = self.client.open(
            '/report',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_report_id_get(self):
        """Test case for report_id_get

        [Unimplemented] Returnsreport data
        """
        response = self.client.open(
            '/report/{id}'.format(id=ID()),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
