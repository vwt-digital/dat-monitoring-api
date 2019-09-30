# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.build_status import BuildStatus  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_build_statusen_get(self):
        """Test case for build_statusen_get

        Get all build statusen
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/build-statusen',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
