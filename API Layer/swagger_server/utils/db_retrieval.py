
"""
    This module contains the functions that interact with the database to retrieve information.
"""

from swagger_server.utils import connection_utils
from psycopg2.errors import RaiseException
from datetime import datetime

db_connection = connection_utils.DBConnection()
kb_connection = connection_utils.DBConnection(connection_utils.KB_HOST, 
                                              connection_utils.KB_NAME, 
                                              connection_utils.KB_ACCESS_NAME, 
                                              connection_utils.KB_ACCESS_PASSWORD, 
                                              connection_utils.KB_PORT,
                                              connection_utils.kb_init_file,
                                              'kb')

def get_machine_status(machines=None):
    """
        Get the status of the machines given their ids

        :param machines: Specific machines to restrict the query to
        :type machines: List[int]

        :return: The status of the machines and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: List[(int, str)], int | str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_machine_status', [machines])
            # prepare JSON response
            res = []
            for record in cursor.fetchall():
                item = {}
                item['id'] = record[0]
                item['status'] = record[1]
                res.append(item)
            return res, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500

def get_machine_info(machines=None, machine_types=None, production_lines=None, factories=None):
    """
        Get information on machines optionally filtered by machines, machine types, production lines and factories

        :param machines: Specific machines to restrict the query to
        :type machines: List[int]
        :param machine_types: Specific machine types to restrict the query to
        :type machine_types: List[str]
        :param production_lines: Specific production lines to restrict the query to
        :type production_lines: List[int]
        :param factories: Specific factories to restrict the query to
        :type factories: List[str]

        :return: The information on the machines and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: List[{'id': int, 'name': str, 'productionLine': int, 'factory': str, 'machineType': str}], int | str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_machines', [machines, machine_types, production_lines, factories])
            # prepare JSON response
            res = []
            for record in cursor.fetchall():
                item = {'id': record[0], 'name': record[1], 'productionLine': record[2], 'factory': record[3], 'machineType': record[4]}
                res.append(item)
            return res, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500
    
def get_machine_info_with_status(machines=None, machine_types=None, production_lines=None, factories=None, status=None):
    """
        Get information on machines with status optionally filtered by machines, machine types, production lines, factories and status

        :param machines: Specific machines to restrict the query to
        :type machines: List[int]
        :param machine_types: Specific machine types to restrict the query to
        :type machine_types: List[str]
        :param production_lines: Specific production lines to restrict the query to
        :type production_lines: List[int]
        :param factories: Specific factories to restrict the query to
        :type factories: List[str]
        :param status: Specific status to restrict the query to
        :type status: str

        :return: The information on the machines with status and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: List[{'id': int, 'name': str, 'productionLine': int, 'factory': str, 'machineType': str, 'status': str}], int | str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_machines_with_status', [machines, machine_types, production_lines, factories, status])
            # prepare JSON response
            res = []
            for record in cursor.fetchall():
                item = {"id": record[0], "factory": record[3], "machineType": record[4], "name": record[1], "productionLine": record[2], "status": record[5]}
                res.append(item)
            return res, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500
    
def add_machine(name, production_line, factory, machine_type):
    """
        Add a machine to the database

        :param name: The name of the machine
        :type name: str
        :param production_line: The production line of the machine
        :type production_line: int
        :param factory: The factory of the machine
        :type factory: str
        :param machine_type: The type of the machine
        :type machine_type: str

        :return: The id of the newly inserted machine and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: int, int | str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('insert_machine', [name, production_line, factory, machine_type])
            # Get the id of the newly inserted machine
            id = cursor.fetchone()[0]
            if id == -1:
                return 'Machine name already exists', 400
            return id, 201
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500
    
def update_machine(machine_id, name=None, production_line=None, factory=None, machine_type=None):
    """
        Update a machine in the database

        :param machine_id: The id of the machine to update
        :type machine_id: int
        :param name: The new name of the machine
        :type name: str
        :param production_line: The new production line of the machine
        :type production_line: int
        :param factory: The new factory of the machine
        :type factory: str
        :param machine_type: The new type of the machine
        :type machine_type: str

        :return: The operation message and the operation status code
        :rtype: str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('update_machine', [machine_id, name, production_line, factory, machine_type])
            id = cursor.fetchone()[0]
            if id == -1:
                return 'Machine updated name already exists', 400
            return 'Success', 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500

def delete_machine(machine_id):
    """
        Delete a machine from the database

        :param machine_id: The id of the machine to delete
        :type machine_id: int

        :return: The operation message and the operation status code
        :rtype: str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('delete_machine', [machine_id])
            if cursor.fetchone()[0] == -1:
                return 'Machine not found', 404
            return 'Success', 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500
    
def get_alert_info(alert_id=None):
    """
        Get information on alerts given their ids

        :param alert_id: Specific alerts to restrict the query to
        :type alert_id: List[int]

        :return: The information on the alerts and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: List[{'id': int, 'machineID': int, 'timestamp': str, 'severity': str, 'kpi': str, 'alertDescription': str}], int | str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_alerts', [alert_id])
            # prepare JSON response
            res = []
            for record in cursor.fetchall():
                item = {}
                item['id'] = record[0]
                item['machineID'] = record[1]
                item['timestamp'] = datetime.strftime(record[2], '%Y-%m-%d %H:%M:%S')
                if record[3] == 1:
                    item['severity'] = 'low'
                if record[3] == 2:
                    item['severity'] = 'medium'
                if record[3] == 3:
                    item['severity'] = 'high'
                item['kpi'] = record[4]
                item['alertDescription'] = record[5]
                res.append(item)
            return res, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500
    
def get_alerts_filtered(machines=None, severity=None, start_time=None, end_time=None):
    """
        Get filtered information on alerts optionally restricted by machines, severity and time window

        :param machines: Specific machines to restrict the query to
        :type machines: List[int]
        :param severity: Specific severity to restrict the query to
        :type severity: str
        :param start_time: The start time of the alerts
        :type start_time: str
        :param end_time: The end time of the alerts
        :type end_time: str

        :return: The filtered information on the alerts and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: List[{'alertDescription': str, 'id': int, 'kpi': str, 'machineID': int, 'severity': str, 'timestamp': str}], int | str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_alerts_filtered', [machines, severity, start_time, end_time])
            # prepare JSON response
            res = []
            for record in cursor.fetchall():
                item = {}
                item['alertDescription'] = record[4]
                item['id'] = record[0]
                item['kpi'] = record[5]
                item['machineID'] = record[2]
                if record[3] == 1:
                    item['severity'] = 'low'
                if record[3] == 2:
                    item['severity'] = 'medium'
                if record[3] == 3:
                    item['severity'] = 'high'
                item['timestamp'] = datetime.strftime(record[1], '%Y-%m-%d %H:%M:%S')
                res.append(item)
            return res, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500
    
def add_alert(machine_id, severity, description, timestamp, kpi):
    """
        Add an alert to the database

        :param machine_id: The id of the machine
        :type machine_id: int
        :param severity: The severity of the alert
        :type severity: str
        :param description: The description of the alert
        :type description: str
        :param timestamp: The timestamp of the alert
        :type timestamp: str
        :param kpi: The KPI of the alert
        :type kpi: str

        :return: The id of the newly inserted alert and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: int, int | str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('insert_alert', [machine_id, timestamp, severity, kpi, description])
            index = cursor.fetchone()[0]
            if index is None:
                return 'Invalid parameters', 400
            return index, 201
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Invalid parameters', 400
        finally:
            cursor.close()
    else:
        return 'Connection error', 500
    
def get_sensor_data(machines=None, _from=None, to=None, dataTypes=None, aggregationType='sum'):
    """
        Get raw sensor data optionally filtered by machines, time, data types using a specific aggregation type

        :param machines: Specific machines to restrict the query to
        :type machines: List[int]
        :param _from: The start time of the data
        :type _from: str
        :param to: The end time of the data
        :type to: str
        :param dataTypes: Specific kpis to restrict the query to
        :type dataTypes: List[str]
        :param aggregationType: The aggregation type of the data
        :type aggregationType: str

        :return: The raw sensor data and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: List[{'machine_id': int, 'KPI': str, 'timestampSeries': List[str], 'valueSeries': List[float]}], int | str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_sensor_data', [_from, to, machines, dataTypes, aggregationType])
            res = {}
            # fill the response with the data
            for record in cursor.fetchall():
                cur_machine = record[0]
                cur_kpi = record[2]
                if (cur_machine, cur_kpi) not in res:
                    res[(cur_machine, cur_kpi)] = {'timestampSeries': [], 'valueSeries': []}
                res[(cur_machine, cur_kpi)]['timestampSeries'].append(datetime.strftime(record[1], '%Y-%m-%d %H:%M:%S'))
                res[(cur_machine, cur_kpi)]['valueSeries'].append(record[3])

            # explode index
            res = [{'machineID': k[0], 'kpi': k[1], 'timestampSeries': v['timestampSeries'], 'valueSeries': v['valueSeries']} for k, v in res.items()]
            return res, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500
    
def get_preprocessed_data(machines=None, _from=None, to=None, dataTypes=None, aggregationType='sum'):
    """
        Get preprocessed sensor data optionally filtered by machines, time, data types using a specific aggregation type

        :param machines: Specific machines to restrict the query to
        :type machines: List[int]
        :param _from: The start time of the data
        :type _from: str
        :param to: The end time of the data
        :type to: str
        :param dataTypes: Specific kpis to restrict the query to
        :type dataTypes: List[str]
        :param aggregationType: The aggregation type of the data
        :type aggregationType: str

        :return: The preprocessed sensor data and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: List[{'machine_id': int, 'KPI': str, 'timestampSeries': List[str], 'valueSeries': List[float]}], int | str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_preprocessed_data', [_from, to, machines, dataTypes, aggregationType])
            res = {}
            # fill the response with the data
            for record in cursor.fetchall():
                cur_machine = record[0]
                cur_kpi = record[2]
                if (cur_machine, cur_kpi) not in res:
                    res[(cur_machine, cur_kpi)] = {'timestampSeries': [], 'valueSeries': []}
                res[(cur_machine, cur_kpi)]['timestampSeries'].append(datetime.strftime(record[1], '%Y-%m-%d %H:%M:%S'))
                res[(cur_machine, cur_kpi)]['valueSeries'].append(record[3])

            # explode index
            res = [{'machineID': k[0], 'kpi': k[1], 'timestampSeries': v['timestampSeries'], 'valueSeries': v['valueSeries']} for k, v in res.items()]
            return res, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500
    
def get_machine_name_by_id(machine_id):
    """
        Get the name of a machine given its id

        :param machine_id: The id of the machine
        :type machine_id: int

        :return: The name of the machine if successful, None otherwise
        :rtype: str | None
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_machine_name', [machine_id])
            record = cursor.fetchone()
            return record[0]
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return None
        finally:
            cursor.close()
    else:
        return None

def add_sensor_data_to_kafka(machine_id, kpi_id, aggregationTypeList, values):
    """
        Add sensor data to the Kafka topic for the given machine and KPI with multiple aggregation types and values.
        The i-th element of aggregationTypeList corresponds to the i-th element of values.

        :param machine_id: The id of the machine
        :type machine_id: int
        :param kpi_id: The id of the KPI
        :type kpi_id: str
        :param aggregationTypeList: The list of aggregation types
        :type aggregationTypeList: List[str]
        :param values: The list of values
        :type values: List[float]

        :return: The operation message and the operation status code
        :rtype: str, int
    """
    # check for machine existence
    machine_name = get_machine_name_by_id(machine_id)
    if machine_name is None:
        return 'Machine not found', 404
    length = min(len(aggregationTypeList), len(values))
    connection_utils.add_element_to_kafka({kpi_id: {aggregationTypeList[i]: values[i] for i in range(length)}}, machine_id)
    return 'Success', 200

def get_machine_type_from_id(machine_id):
    """
        Get the type of a machine given its id

        :param machine_id: The id of the machine
        :type machine_id: int

        :return: The type of the machine and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_machine_type', [machine_id])
            machine_type = cursor.fetchone()[0]
            if machine_type is None:
                return 'Machine not found', 404
            return machine_type, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return "Execution error", 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500

def get_kpi_list_from_machine_type(machine_type):
    """
        Get the list of KPIs given a machine type

        :param machine_type: The type of the machine
        :type machine_type: str

        :return: The list of KPIs and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: List[str], int | str, int
    """
    # get KPI list from Knowledge Base
    cursor = kb_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_kpi_list_from_machine_type', [machine_type])
            # prepare JSON response
            res = []
            for record in cursor.fetchall():
                res.append(record[0])
            return res, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500

def kpi_exists(kpi_id):
    """
        Check the existence of a KPI in the Knowledge Base

        :param kpi_id: The id of the KPI
        :type kpi_id: str

        :return: True if the KPI exists, False if the KPI doesn't exist and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: bool, int | str, int
    """
    cursor = kb_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('kpi_exists', [kpi_id])
            return cursor.fetchone()[0], 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500

def allowed_kpi_machine(machine_id, kpi):
    """
        Check if a machine can produce a specific KPI

        :param machine_id: The id of the machine
        :type machine_id: int
        :param kpi: The KPI
        :type kpi: str

        :return: True if the machine can produce the KPI, False if the machine can't produce the KPI and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: bool, int | str, int
    """
    # get machine type
    machine_type, status = get_machine_type_from_id(machine_id)
    if status != 200:
        return machine_type, status#returns the error message
    # check existence of KPI in Knowledge Base
    res, status = kpi_exists(kpi)
    if status != 200:
        return res, status
    elif not res:
        return 'KPI not found', 404
    # get KPI list from Knowledge Base
    kpi_list, status = get_kpi_list_from_machine_type(machine_type)
    if status != 200:
        return kpi_list, status
    if kpi in kpi_list:
        return True, 200
    return False, 200

def get_kpi_list_from_machine_id(machine_id):
    """
        Get the list of KPIs given a machine id

        :param machine_id: The id of the machine
        :type machine_id: int

        :return: The list of KPIs and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: List[str], int | str, int
    """
    # get machine type
    machine_type, status = get_machine_type_from_id(machine_id)
    if status != 200:
        return machine_type, status
    # get KPI list from Knowledge Base
    return get_kpi_list_from_machine_type(machine_type)

def get_kpi_list(kpi_filter=None, category_filter=None):
    """
        Get the list of KPIs optionally filtered by KPI name and category

        :param kpi_filter: Specific KPIs to restrict the query to
        :type kpi_filter: List[str]
        :param category_filter: Specific categories to restrict the query to
        :type category_filter: List[str]

        :return: The list of KPIs and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: List[{'nameID': str, 'description': str, 'category': str, 'unit': str, 'formula': str, 'relationNumber': int}], int | str, int
    """
    cursor = kb_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_kpi_list', [kpi_filter, category_filter])
            # prepare JSON response
            res = []
            for record in cursor.fetchall():
                item = {"nameID": record[0], "description": record[1], "category": record[2], "unit": record[3], "formula": record[4], "relationNumber": record[5]}
                res.append(item)
            return res, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500
    
def get_kpi_machine_types(kpi_id):
    """
        Get the machine types that can produce a specific KPI

        :param kpi_id: The id of the KPI
        :type kpi_id: str

        :return: The machine types that can produce the KPI and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: List[str], int | str, int
    """
    cursor = kb_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_machine_type_list_from_kpi', [kpi_id])
            # prepare JSON response
            res = []
            for record in cursor.fetchall():
                res.append(record[0])
            return res, 200
        except Exception as e:
            if isinstance(e, RaiseException):
                return 'KPI not found', 404
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500

def get_machine_id_and_name_from_types(machine_types):
    """
        Get the ids and names of the machines given their types

        :param machine_types: Specific machine types to restrict the query to
        :type machine_types: List[str]

        :return: The ids and names of the machines and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: {'ids': List[int], 'names': List[str]}, int | str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_machine_ids_and_name_from_types', [machine_types])
            # prepare JSON response
            res_ids = []
            res_names = []
            for record in cursor.fetchall():
                res_ids.append(record[0])
                res_names.append(record[1])
            return {'ids': res_ids, 'names': res_names}, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500

def get_machines_by_kpi(kpi_id):
    """
        Get the machines that can produce a specific KPI

        :param kpi_id: The id of the KPI
        :type kpi_id: str

        :return: The machines that can produce the KPI and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: {'ids': List[int], 'names': List[str]}, int | str, int
    """
    # get machine types
    machine_types, status = get_kpi_machine_types(kpi_id)
    if status != 200:
        return machine_types, status
    # get machines
    return get_machine_id_and_name_from_types(machine_types)

# Unused
def get_machines_info_not_in_list(machine_ids):
    """
        Get information on machines not in a given list

        :param machine_ids: Specific machines to exclude from the query
        :type machine_ids: List[int]

        :return: The information on the machines not in the list and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: List[{'id': int, 'name': str, 'productionLine': int, 'factory': str, 'machineType': str}], int | str, int
    """
    cursor = db_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_machines_not_in_list', [machine_ids])
            # prepare JSON response
            res = []
            for record in cursor.fetchall():
                item = {'id': record[0], 'name': record[1], 'productionLine': record[2], 'factory': record[3], 'machineType': record[4]}
                res.append(item)
            return res, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500

# Unused
def get_kpi_info_not_in_list(kpi_name_ids):
    """
        Get information on KPIs not in a given list

        :param kpi_name_ids: Specific KPIs to exclude from the query
        :type kpi_name_ids: List[str]

        :return: The information on the KPIs not in the list and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: List[{'nameID': str, 'description': str, 'category': str, 'unit': str, 'formula': str, 'relationNumber': int}], int | str, int
    """
    cursor = kb_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_kpi_info_not_in_list', [kpi_name_ids])
            # prepare JSON response
            res = []
            for record in cursor.fetchall():
                item = {"nameID": record[0], "description": record[1], "category": record[2], "unit": record[3], "formula": record[4], "relationNumber": record[5]}
                res.append(item)
            return res, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500

# Returns informations on machines, KPIs and the relation between them
def get_machine_xkpi_info():
    """
        Get information on machines, KPIs and the relation between them.
        The relation between machines and KPIs is based on the machine type and is expressed as couples of machine ids and a numerical id of the KPIs (called relatioNumber in KPIs info).

        :return: The information on the machines, KPIs and the relation between them and the operation status code if successful, an error message and the operation status code otherwise
        :rtype: {'machines': List[{'id': int, 'name': str, 'productionLine': int, 'factory': str, 'machineType': str}], 'kpis': List[{'nameID': str, 'description': str, 'category': str, 'unit': str, 'formula': str, 'relationNumber': int}], 'relation': List[{'machineID': int, 'kpiID': int}]}, int | str, int
    """
    res = {}
    # Get machines info
    machines_info, status = get_machine_info()
    if status != 200:
        return machines_info, status
    res['machines'] = machines_info
    # Get KPIs info
    kpis_info, status = get_kpi_list()
    if status != 200:
        return kpis_info, status
    res['kpis'] = kpis_info
    # Get relation between machines and KPIs
    # prepare type to id dictionary
    type_to_id = {}
    for machine in machines_info:
        if machine['machineType'] not in type_to_id:
            type_to_id[machine['machineType']] = []
        type_to_id[machine['machineType']].append(machine['id'])

    cursor = kb_connection.get_cursor()
    if cursor is not None:
        try:
            cursor.callproc('get_machine_kpi_relation', [list(type_to_id.keys())])
            # prepare JSON response
            temp = []
            for record in cursor.fetchall():
                for machine_id in type_to_id[record[0]]:
                    temp.append({"machineID": machine_id, "kpiID": record[1]})
            res['relation'] = temp
            return res, 200
        except Exception as e:
            print("Something went wrong when executing the stored procedure: ", e, flush=True)
            return 'Execution error', 500
        finally:
            cursor.close()
    else:
        return 'Connection error', 500
    