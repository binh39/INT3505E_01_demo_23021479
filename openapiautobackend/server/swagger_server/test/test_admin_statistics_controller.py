# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.statistics import Statistics  # noqa: E501
from swagger_server.test import BaseTestCase


class TestAdminStatisticsController(BaseTestCase):
    """AdminStatisticsController integration test stubs"""

    def test_api_statistics_get(self):
        """Test case for api_statistics_get

        Get product and inventory statistics (Admin only)
        """
        response = self.client.open(
            '/api/statistics',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
