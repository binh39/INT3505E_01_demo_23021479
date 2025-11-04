# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from swagger_server.models.inline_response2002 import InlineResponse2002  # noqa: E501
from swagger_server.models.login_request import LoginRequest  # noqa: E501
from swagger_server.models.login_response import LoginResponse  # noqa: E501
from swagger_server.models.logout_request import LogoutRequest  # noqa: E501
from swagger_server.models.refresh_request import RefreshRequest  # noqa: E501
from swagger_server.models.refresh_response import RefreshResponse  # noqa: E501
from swagger_server.test import BaseTestCase


class TestAuthenticationController(BaseTestCase):
    """AuthenticationController integration test stubs"""

    def test_api_sessions_delete(self):
        """Test case for api_sessions_delete

        Logout
        """
        body = LogoutRequest()
        response = self.client.open(
            '/api/sessions',
            method='DELETE',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_sessions_me_get(self):
        """Test case for api_sessions_me_get

        Verify token and get user info
        """
        response = self.client.open(
            '/api/sessions/me',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_sessions_post(self):
        """Test case for api_sessions_post

        User login
        """
        body = LoginRequest()
        response = self.client.open(
            '/api/sessions',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_sessions_refresh_post(self):
        """Test case for api_sessions_refresh_post

        Refresh access token
        """
        body = RefreshRequest()
        response = self.client.open(
            '/api/sessions/refresh',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_root_get(self):
        """Test case for root_get

        Root endpoint with API information
        """
        response = self.client.open(
            '/',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
