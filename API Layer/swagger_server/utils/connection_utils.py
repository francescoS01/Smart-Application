
"""
    This module is used to define the connection parameters for the sensors database, the knowledge base database and kafka.
    It contains the class DBConnection to handle the connection to databases, initialize stored procedures
    and execute queries.
    The module also contains the function add_element_to_kafka to add a measurement to a Kafka topic.
"""
# the import swagger_server.ext can be resolved in the docker container
from swagger_server.ext import kafka # type: ignore

import json
import psycopg2
from datetime import datetime
from enum import Enum

PORT_API = 443

DB_PORT = 5432
DB_HOST = 'db'
DB_ACCESS_NAME = 'postgres'
DB_ACCESS_PASSWORD = 'password'#TODO: change to env variable
DB_NAME = 'postgres'

KB_HOST = 'kb'
KB_PORT = 5432
KB_ACCESS_NAME = 'postgres'
KB_ACCESS_PASSWORD = 'password'#TODO: change to env variable
KB_NAME = 'postgres'

KAFKA_TOPIC = 'measurements'

'''
    Enum to define opeartion results.
'''
class OperationResult(Enum):
    SUCCESS = 0
    CONNECTION_ERROR = 1
    EXECUTION_ERROR = 2

init_status = {
    'db': False,
    'kb': False
}
db_init_file = './swagger_server/utils/db_utils/db_procedures_init.sql'
kb_init_file = './swagger_server/utils/db_utils/kb_procedures_init.sql'
    
class DBConnection:
    """
        Class to handle the connection to the database.

        :param host: The host of the database.
        :type host: str
        :param database: The name of the database.
        :type database: str
        :param user: The user to access the database.
        :type user: str
        :param password: The password to access the database.
        :type password: str
        :param port: The port to access the database.
        :type port: int
        :param init_file: The file containing the initialization scripts for the DB required for the API
        :type init_file: str
        :param init_status_key: The key to access the status of the initialization of the DB
        :type init_status_key: str
    """
    def __init__(self, 
                 host=DB_HOST, 
                 database=DB_NAME, 
                 user=DB_ACCESS_NAME, 
                 password=DB_ACCESS_PASSWORD, 
                 port=DB_PORT,
                 init_file=db_init_file,
                 init_status_key='db'):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self._init_file = init_file
        self._init_status_key = init_status_key
        self._conn = None

    def _connect(self):
        """
            Connect to the database and initialize it if it has not been initialized yet.

            :return: None
            :rtype: None
        """
        if self._conn is None:
            print("Connecting to the database", self.database, "on host", self.host, flush=True)
            self._conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
            )
            print("Connected to the database", self.database, "on host", self.host, flush=True)
            self._conn.autocommit = True
            if not init_status[self._init_status_key]:
                self._init_db()
                init_status[self._init_status_key] = True

    def _init_db(self):
        """
            Initialize the database by executing the initialization scripts.

            :return: None
            :rtype: None
        """
        # Execute sql scripts in db_utils folder
        with open(self._init_file, 'r') as file:
            cursor = self._conn.cursor()
            init_sql = file.read()
            cursor.execute(init_sql)

    def get_cursor(self):
        """
            Attempt to connect to the database and return the cursor object.
            If the connection cannot be established, return None.

            :return: The cursor object or None
            :rtype: psycopg2.extensions.cursor | None
        """
        
        try:
            self._connect()
            return self._conn.cursor()
        except Exception as e:
            print("Something went wrong when connecting to the database: ", e)
            self.close_connection()
            return None

    def close_connection(self):
        """
            Close the connection to the database.

            :return: None
            :rtype: None
        """
        try:
            if self._conn is not None:
                self._conn.close()
        except Exception as e:
            pass
        self._conn = None

    def execute_query(self, query):
        """
            Execute a query on the database.

            :param query: The query to execute.
            :type query: str
            :return: The result of the operation and the fetched data.
            :rtype: OperationResult, list | None
        """
        with self.get_cursor() as cursor:
            if cursor is None:
                return OperationResult.CONNECTION_ERROR, None
            try:
                cursor.execute(query)
            except Exception as e:
                return OperationResult.EXECUTION_ERROR, None
            return OperationResult.SUCCESS, cursor.fetchall()
    

def add_element_to_kafka(measurement_json, machine_id):
    """
        Add a measurement to the Kafka topic.

        :param measurement_json: The measurement to add in JSON format.
        :type measurement_json: dict
        :param machine_id: The ID of the machine.
        :type machine_id: int
        :return: None
        :rtype: None
    """
    kafka.put_message(kafka.get_producer(), KAFKA_TOPIC, str(machine_id), json.dumps({'machine': machine_id, 'measurement': measurement_json}))