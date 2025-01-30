from MOCK_Knowledge_base.KB import get_KB
import requests
# simulate checking with the ontology if calculations requested are actually possible
class KnowledgeBaseInterface:

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
    

    
    #Serve? Dipende dal gruppo 1
    def check_kpi_availability(machine_id:int,kpis:list[str]):
        result=requests.get(f"https://api-layer/machine/{machine_id}/KPIList",verify=False)

        machine_kpis=result.json()

        is_computable=all(
            map(
                lambda x: x in machine_kpis,
                kpis
            )
        )
        return is_computable
    def retrieve_kpi_data(kpis:list[str]):
        kpis_info=list()
        for kpi in kpis:
            result=requests.get(f"https://api-layer/KPI/{kpi}", verify=False)
            infos=result.json()
            kpis_info.append(infos)
        return kpis_info
    def calculate_unit(units:set[str]):
        units.discard('?')
        if len(units) == 1:
            return units[0]
        else:
            return '?'

