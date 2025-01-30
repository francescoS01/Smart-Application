import requests
from MOCK_Knowledge_base.KB import get_KB

BASE_URL='https://api-layer'

AUTH_URL = f'{BASE_URL}/user/login'

YOUR_USERNAME='admin'
YOUR_PASSWORD='admin'

auth_token = None

def get_token(url, username, password):
    headers = {
        'username': username,
        'password': password
    }  
    response = requests.post(url, headers=headers, verify=False)
    if response.status_code == 200:
        print('You are authenticated!')
        return response.json()
    elif response.status_code == 400:
        print('Wrong credentials')
    elif response.status_code == 500:
        print('Connection error')
    else:
        print('Unknown error')
    return None

auth_token = get_token(AUTH_URL, YOUR_USERNAME, YOUR_PASSWORD)

def call_with_token(url, token, call_type='GET', header_params=None):
    headers = {} if header_params is None else header_params
    headers['Authorization'] = token
    if call_type == 'GET':
        response = requests.get(url, headers=headers, verify=False)
    elif call_type == 'POST':
        response = requests.post(url, headers=headers, verify=False)
    elif call_type == 'PUT':
        response = requests.put(url, headers=headers, verify=False)
    elif call_type == 'DELETE':
        response = requests.delete(url, headers=headers, verify=False)
    else:
        print('Unknown call type')
        return None, None
    if response.status_code == 500:
        print('Server error: ', response.reason)
        return None, response.status_code
    elif response.status_code == 400:
        print('Bad request: ', response.reason)
        return None, response.status_code
    elif response.status_code == 401:
        print('Unauthorized')
        return None, response.status_code
    elif response.status_code == 200:
        return response.json(), response.status_code
    else:
        print('Unknown error: ', response.reason)
        return None, response.status_code

def call_and_retry(url, token, call_type='GET', header_params=None):
    response, status = call_with_token(url, token, call_type, header_params)
    if status == 401:
        print('Token expired, getting new token')
        token = get_token(AUTH_URL, YOUR_USERNAME, YOUR_PASSWORD)
        if token is None:
            print('Failed to get new token')
            return None, 401
        return call_and_retry(url, token, call_type, header_params)
    return response, status


# simulate checking with the ontology if calculations requested are actually possible
class KnowledgeBaseInterface:
    #mocked requests
    __KB = get_KB()
    
    __units = {
            'working_time': "seconds",
            'cost_idle': "euro",
            'bad_cycles': "#",
            'cost': "euro per kWh",
            'power': "kW",
            'good_cycles': "#",
            'consumption': "kWh",
            'idle_time': "seconds",
            'average_cycle_time': "seconds",
            'cost_working': "euro",
            'consumption_working': "kWh",
            'offline_time': "seconds",
            'cycles': "#",
            'consumption_idle': "kWh"
        }
    
    def unit(kpi):
        try: return KnowledgeBaseInterface.__units[kpi]
        except: return "?"

    def get_machine(machine_id):
        machines = [
            (key, machine)
            for key, machine in KnowledgeBaseInterface.__KB.nodes(data=True)
            if (
                (machine.get("node_type") == "Machine")
                and (machine.get("id") == machine_id)
            )
        ]
        return machines[0] if len(machines) != 0 else None

    def get_kpi(kpi):
        KPIs = [
            (key, kpi_v)
            for key, kpi_v in KnowledgeBaseInterface.__KB.nodes(data=True)
            if (kpi_v.get("node_type") == "KPI" and key == kpi)
        ]
        return KPIs[0] if len(KPIs) != 0 else None
    
    #Serve? Dipende dal gruppo 1
    def check_validity(machine_id, kpi, operation):
        machine_key, machine_node = KnowledgeBaseInterface.get_machine(machine_id)
        if machine_node is None:
            return False
        kpi_key, kpi_node = KnowledgeBaseInterface.get_kpi(kpi)
        if kpi_node is None:
            return False
        operations_available = KnowledgeBaseInterface.__KB.get_edge_data(
            machine_key, kpi_key, "operation"
        )
        if not operations_available:
            return False
        if operations_available["operation"] != operation:
            return False
        return True
    

    # non mocked requests
    def check_kpi_availability(machine_id:int,kpis:list[str]):
        token=get_token(AUTH_URL,YOUR_USERNAME,YOUR_PASSWORD)


        KPI_LIST_URL=f'{BASE_URL}/machine/{machine_id}/KPIList'
        machine_kpis,code_status=call_and_retry(KPI_LIST_URL,token)
        if machine_kpis is None:
            return False

        is_computable=all(
            map(
                lambda x: x in machine_kpis,
                kpis
            )
        )
        return is_computable

    def retrieve_kpi_data(kpis:list[str]):
        token=get_token(AUTH_URL,YOUR_USERNAME,YOUR_PASSWORD)
        kpis_info=list()
        for kpi in kpis:
            KPI_LIST_URL=f'{BASE_URL}/KPI/{kpi}'
            kpi_data,code_status=call_and_retry(KPI_LIST_URL,token)
            if not kpi_data is None:
                kpis_info.append(kpi_data)
        return kpis_info
    
    def calculate_unit(units:set[str]):
        units.discard('?')
        if len(units) == 1:
            return units[0]
        else:
            return '?'