from enum import Enum
from typing import List, Optional
from pydantic import BaseModel,Field
from datetime import datetime,timedelta

from .common_models import AggregationOperation, CalculationResponse,Units,BASEKPINames,CalculationCodes

class CalculationAlertResponse(CalculationResponse):
    result: Optional[bool] = Field(
        description="a boolean saying if the alert is fired according to the expression and time range specified"
    )


class AddAlertRequest(BaseModel):

    machine_id:int=Field(
        description="the id of the machine for which we want the alert"
    )

    expression:str=Field(
        description="the expression for the alert"
    )

    sliding_window_seconds:float=Field(
        description="the sliding window to calculate values"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "machine_id": 2,
                    "expression": "sum(cycles)>50",
                    "sliding_window_seconds": 10000,
                 }
            ]
        }
    }



class KPIAlertRequest(BaseModel):
    machine_id: int = Field(
        description="The machine id"
    )
    operation: AggregationOperation = Field(
        default=AggregationOperation.SUM,
        description="The internal aggregation operation"
    )

    expression: str = Field(
        ...,
        description="The alert expression to be calculated"

    )
    start_date: datetime = Field(
        description="Starting date in iso format",
        default=datetime.now()-timedelta(days=7)

    )
    end_date: datetime = Field(
        description="Ending date in iso format",
        default=datetime.now()
    )
class RemoveAlertsRequest(BaseModel):
    alerts_ids:List[str]=Field(
        description="a list of the ids of the alerts you want to remove",
        default=[]
    )

class MonitorAlertsResponse(BaseModel):
    monitorUUID:any=Field(
        description="the unique id for the alert"
    )
    timeWindow:float=Field(
        description="the sliding window size"
    )
    expression:str=Field(
        description="the expression to be calculated"
    )
    machineID:int=Field(
        description="the id of the machine referred by the alert"
    )

class AddAlertMonitorResponse(BaseModel):
    new_id:str=Field(
        description=""
    )
