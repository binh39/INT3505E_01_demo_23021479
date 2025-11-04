# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "swagger_server"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion",
    "swagger-ui-bundle>=0.0.2"
]

setup(
    name=NAME,
    version=VERSION,
    description="Product Management System API",
    author_email="support@product.com",
    url="",
    keywords=["Swagger", "Product Management System API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    RESTful API for Product Management with JWT Authentication and HATEOAS principles 1. Login: POST /api/sessions → Nhận access_token (5 phút) và refresh_token (1 giờ) 2. Sử dụng API: Gửi &#x60;Authorization: Bearer {access_token}&#x60; trong header 3. Refresh: POST /api/sessions/refresh khi access_token hết hạn 4. Logout: DELETE /api/sessions → Blacklist access token và revoke refresh token - admin: Full access (CRUD products, statistics, manage inventory) - user: View products only Demo Accounts - Admin: &#x60;admin&#x60; / &#x60;admin123&#x60; - User: &#x60;user&#x60; / &#x60;user123&#x60; 
    """
)
