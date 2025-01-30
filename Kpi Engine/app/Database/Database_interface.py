from datetime import datetime
import numpy as np
import pandas as pd
from utils.utils import call_and_retry, BASE_URL
from typing import List
from pprint import pprint
DB_URL=f"{BASE_URL}/data/preprocessed"

class DBConnection:

    def retrieve_data_db(machine:int, KPIs:List[str], aggregation_operation:str,range:tuple)->tuple:
        """
        retrieve specified data from the db in a certain time range

        Args:
            machine: the machine for which the data is reuqested
            KPIs: the KPIs for which data is requested
            aggregation_operation: the aggregation operation used on the data
            range: the time range for which to retrieve data
        """
        if len(KPIs) == 0:
            return dict(), []
        start_time,end_time=range

        machine_kpis,code_status=call_and_retry(
            DB_URL,
            header_params={
                'machines':str(machine),
                'dataTypes': ','.join(KPIs),
                'aggregationSelector':aggregation_operation,
                'from':start_time,
                'to':end_time,
            }
        )
        
        #pprint("RETRIEVING DATA FROM DB",machine_kpis,"requested kpis",KPIs)

        if machine_kpis is None or len(machine_kpis)==0:
            return {kpi:np.array([]) for kpi in KPIs}, []
        result=dict()
        time_data=machine_kpis[0]['timestampSeries'] if (not machine_kpis[0]['timestampSeries'] is None)  else []

        for kpi_data in machine_kpis:
            result[ kpi_data['kpi'] ]=np.array(kpi_data['valueSeries'])

        
        return result,time_data
    
    def get_time_range(time_range: list[str], start_time: datetime, end_time: datetime) -> np.ndarray[datetime]:
        # Define the time range
        start_time = datetime.strptime(start_time,"%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end_time,"%Y-%m-%d %H:%M:%S")
        time_range=list(map(lambda x: datetime.strptime(x,"%Y-%m-%d %H:%M:%S") ,time_range))
        # Filter strings within the time range
        filtered_times = [
            timestamp_point for timestamp_point in time_range
            if start_time <= timestamp_point <= end_time
        ]
        return np.array(
            list(
                set(
                    filtered_times
                )
            )
        )
