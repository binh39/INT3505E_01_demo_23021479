# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response2003 import InlineResponse2003  # noqa: E501
from swagger_server.models.inline_response2006 import InlineResponse2006  # noqa: E501
from swagger_server.models.products_list_response import ProductsListResponse  # noqa: E501
from swagger_server.test import BaseTestCase


class TestUserProductsController(BaseTestCase):
    """UserProductsController integration test stubs"""

    def test_api_categories_get(self):
        """Test case for api_categories_get

        Get all product categories
        """
        response = self.client.open(
            '/api/categories',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_products_get(self):
        """Test case for api_products_get

        Get all products (with pagination and filtering)
        """
        query_string = [('page', 2),
                        ('limit', 100),
                        ('category', 'category_example'),
                        ('brand', 'brand_example'),
                        ('sku', 'sku_example'),
                        ('status', 'status_example'),
                        ('min_price', 0),
                        ('max_price', 3.4),
                        ('search', 'search_example'),
                        ('sort', 'created_at')]
        response = self.client.open(
            '/api/products',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_products_product_id_get(self):
        """Test case for api_products_product_id_get

        Get product details by ID
        """
        response = self.client.open(
            '/api/products/{product_id}'.format(product_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
