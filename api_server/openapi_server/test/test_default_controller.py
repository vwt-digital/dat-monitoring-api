# coding: utf-8

from __future__ import absolute_import
import unittest
import config

from openapi_server.models.build_trigger_status import BuildTriggerStatus  # noqa: E501
from openapi_server.models.error_report_count import ErrorReportCount  # noqa: E501
from openapi_server.models.error_report_response import ErrorReportResponse  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_build_statuses_triggers_get(self):
        """Test case for build_statuses_triggers_get

        Get all build trigger statuses
        """
        headers = { 
            'Accept': 'application/json',
            "x-api-key": config.API_KEY,
        }
        response = self.client.open(
            '/build-statuses-triggers',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_error_reports_counts_get(self):
        """Test case for error_reports_counts_get

        Get count of project errors reportings in last x days
        """
        headers = { 
            'Accept': 'application/json',
            "x-api-key": config.API_KEY,
        }
        response = self.client.open(
            '/error-reports/counts?days={days}&max_rows={max_rows}'.format(days=7, max_rows=5),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_error_reports_get(self):
        """Test case for error_reports_get

        Get errors reportings
        """
        headers = { 
            'Accept': 'application/json',
            "x-api-key": config.API_KEY,
        }
        response = self.client.open(
            '/error-reports?page_size={page_size}&page={page}'.format(page_size=5, page='next'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
