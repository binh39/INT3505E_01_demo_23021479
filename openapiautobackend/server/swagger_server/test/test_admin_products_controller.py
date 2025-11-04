# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.create_product_request import CreateProductRequest  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response2003 import InlineResponse2003  # noqa: E501
from swagger_server.models.inline_response2004 import InlineResponse2004  # noqa: E501
from swagger_server.models.inline_response2005 import InlineResponse2005  # noqa: E501
from swagger_server.models.inline_response2006 import InlineResponse2006  # noqa: E501
from swagger_server.models.inline_response201 import InlineResponse201  # noqa: E501
from swagger_server.models.products_list_response import ProductsListResponse  # noqa: E501
from swagger_server.models.update_product_request import UpdateProductRequest  # noqa: E501
from swagger_server.test import BaseTestCase


class TestAdminProductsController(BaseTestCase):
    """AdminProductsController integration test stubs"""

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

    def test_api_products_post(self):
        """Test case for api_products_post

        Create new product (Admin only)
        """
        body = CreateProductRequest()
        response = self.client.open(
            '/api/products',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_api_products_product_id_delete(self):
        """Test case for api_products_product_id_delete

        Delete product (Admin only)
        """
        response = self.client.open(
            '/api/products/{product_id}'.format(product_id=56),
            method='DELETE')
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

    def test_api_products_product_id_put(self):
        """Test case for api_products_product_id_put

        Update product information (Admin only)
        """
        body = UpdateProductRequest()
        response = self.client.open(
            '/api/products/{product_id}'.format(product_id=56),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
