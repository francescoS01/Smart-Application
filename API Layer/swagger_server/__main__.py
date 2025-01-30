#!/usr/bin/env python3

"""
This is the main module of the API Layer.
A connexion server is started and the swagger.yaml file is used listen to incoming requests on the endpoints defined in the swagger file.
The server uses gevent to handle multiple requests at the same time and Talisman to add security headers to the responses and to enforce HTTPS.
"""

# keep this import order
from gevent import monkey
monkey.patch_all()

import connexion

from swagger_server import encoder
from flask import Flask
from flask_talisman import Talisman
from gevent import pywsgi

import swagger_server.utils.connection_utils

def main():
    app = connexion.App(__name__, specification_dir='./swagger/', server='gevent')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Smart App Group C - API Layer'}, pythonic_params=True)
    talisman = Talisman(app.app, content_security_policy=None)
    app.run(port=swagger_server.utils.connection_utils.PORT_API, keyfile='./swagger_server/key.pem', certfile='./swagger_server/cert.pem', server='gevent')

if __name__ == '__main__':
    main()
