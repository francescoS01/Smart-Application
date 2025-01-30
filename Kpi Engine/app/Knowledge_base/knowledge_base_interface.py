
from utils.utils import call_and_retry, BASE_URL
class KnowledgeBaseInterface:
    def check_kpi_availability(machine_id:int,kpis:list[str]) -> bool:
        KPI_LIST_URL=f'{BASE_URL}/machine/{machine_id}/KPIList'
        machine_kpis,code_status=call_and_retry(KPI_LIST_URL)
        if machine_kpis is None:
            return False

        is_computable=all(
            map(
                lambda x: x in machine_kpis,
                kpis
            )
        )
        return is_computable

    def retrieve_kpi_data(kpis:list[str]) -> list[dict]:
        kpis_info=list()


        for kpi in kpis:
            KPI_LIST_URL=f'{BASE_URL}/KPI/{kpi}'
            kpi_data,code_status=call_and_retry(KPI_LIST_URL)
            if not kpi_data is None:
                kpis_info.append(kpi_data[0])
        return kpis_info
    def retrieve_all_kpi_data() -> list[dict]:
        KPI_LIST_URL=f'{BASE_URL}/KPI'
        kpi_data,code_status=call_and_retry(KPI_LIST_URL)
        return kpi_data
    
    def calculate_unit(units:set[str]) -> str:
        units.discard('?')
        if len(units) == 1:
            return next(iter(units))
        else:
            return '?'
    def get_base_kpis() -> list[str]:
        KPIS_URL=f"{BASE_URL}/KPI"
        kpi_info,code_status=call_and_retry(KPIS_URL)
        base_kpis=[]
        for ki in kpi_info:
            if ki['formula'] is None:
                base_kpis.append(ki['nameID'])
        return base_kpis
    def get_complex_kpis() -> list[str]:
        KPIS_URL=f"{BASE_URL}/KPI"
        kpi_info,code_status=call_and_retry(KPIS_URL)
        base_kpis=[]
        for kpi in kpi_info:
            if not kpi['formula'] is None:
                base_kpis.append(kpi)
        return base_kpis