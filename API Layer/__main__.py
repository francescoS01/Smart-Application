#!/usr/bin/env python3

import connexion

from swagger_server import encoder

import connection_utils

def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Smart App Group C - API Layer'}, pythonic_params=True)
    app.run(port=connection_utils.PORT_API)

if __name__ == '__main__':
    main()
