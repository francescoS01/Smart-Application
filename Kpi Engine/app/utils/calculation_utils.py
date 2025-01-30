from datetime import datetime
from KPI_engine.EngineCalculation.calculation_engine import CalculationEngine
import numpy as np
from utils import utils
import itertools as it

def  calculate_range_kpi(time_range,machine_id:int,expression:str,aggregation:str):
    """
    calculate the kpis in the specified time ranges

    Args:
        time_range: the time segments where the calculation si done
        machine_id: thes id of the machine for which the data is reuested
        expression: the expression to calculate
    Returns:
        a list of the results for each segment
    """
    seg_calculation=[]
    seg_times=[
                (
                    period[0].to_pydatetime().strftime("%Y-%m-%d %H:%M:%S"),

                    period[-1].to_pydatetime().strftime("%Y-%m-%d %H:%M:%S")
                )
                for period in time_range.values()
            ]
    try:
        print(f"""engine inputs
              machine id:{machine_id}
              expression:{expression}
              segmentation passed:{seg_times}
              aggregation:{aggregation}
              """)
        seg_calculation=CalculationEngine.direct_segmented_calculation_KPI(
            machine_id,
            expression,
            seg_times,
            aggregation
        )
        #print("AFTER ENGINE CALCULATION",seg_calculation)
    except Exception as e:
        print("engine error",str(e))
    
    seg_result=list()
    num_results_vals=len(seg_calculation['range'])
    for i in range(num_results_vals):
        start_time=seg_calculation['range'][i][0]    
        end_time=seg_calculation['range'][i][1]
        values= seg_calculation['value'][i]
        values=list(map(utils.remove_nan,values.tolist())) if isinstance(values,np.ndarray) else utils.remove_nan(float(values))
        seg_result.append({
            'start_time':start_time,
            'end_time':end_time,
            'values':values
        })
    
    if all( isinstance(res['values'],list) and len(res['values'])==0 for res in seg_result ):
        seg_result = []

    return seg_result
def calculate_range_alert(start_time:datetime,end_time:datetime,machine_id:int,expression:str):
    """
    calculate the kpis in the specified time ranges

    Args:
        start_time: the initial time for the time range
        end_time: the final time for the time range
        machine_id: thes id of the machine for which the data is reuested
        expression: the expression to calculate
    Returns:
        a boolean
    """
    result=CalculationEngine.direct_calculation_alert(
            machine_id,
            expression,
            start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time.strftime("%Y-%m-%d %H:%M:%S")
    )
    if isinstance(result['values'],np.bool):
        result['values']=bool(result['values'])
    if isinstance(result['values'],list):
        raise ValueError("alert cannot calculate multiple values expression")
    return result['values']



""" print(
    "HARD CODED TESTING",
    CalculationEngine.direct_segmented_calculation_KPI(
            2,
            'cycles',
            [
                ('2024-05-05 00:00:00', '2024-05-12 00:00:00'),
                ('2024-05-12 00:00:00', '2024-05-19 00:00:00'),
                ('2024-05-19 00:00:00', '2024-05-26 00:00:00'),
                ('2024-05-26 00:00:00', '2024-06-02 00:00:00'),
                ('2024-06-02 00:00:00', '2024-06-09 00:00:00'),
                ('2024-06-09 00:00:00', '2024-06-16 00:00:00'),
                ('2024-06-16 00:00:00', '2024-06-23 00:00:00'),
                ('2024-06-23 00:00:00', '2024-06-30 00:00:00'),
                ('2024-06-30 00:00:00', '2024-07-07 00:00:00'),
                ('2024-07-07 00:00:00', '2024-07-14 00:00:00'),
                ('2024-07-14 00:00:00', '2024-07-21 00:00:00'),
                ('2024-07-21 00:00:00', '2024-07-28 00:00:00')
             ],
            'sum'
        )
) """