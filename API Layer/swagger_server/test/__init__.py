"""
This package contains the tests for the swagger_server package.
The tests are written using the pytest framework.
"""
import logging


import pytest
import connexion
#from flask_testing import TestCase

from swagger_server.encoder import JSONEncoder


#class BaseTestCase(TestCase):
#
#    def create_app(self):
#        logging.getLogger('connexion.operation').setLevel('ERROR')
#        app = connexion.App(__name__, specification_dir='../swagger/')
#        app.app.json_encoder = JSONEncoder
#        app.add_api('swagger.yaml')
#        return app.app