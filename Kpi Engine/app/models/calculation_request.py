from enum import Enum
from pydantic import BaseModel,Field
from datetime import datetime,timedelta
from typing import  List, Optional
from .common_models import AggregationOperation, CalculationResponse,Units,BASEKPINames,CalculationCodes


class KPICalculationRequest(BaseModel):
    machine_id: int = Field(
        description="The machine id",
    )
    operation: AggregationOperation = Field(
        default=AggregationOperation.SUM,
        description="The internal aggregation operation"
    )    
    expression: str = Field(
        ...,
        description="The expression to calculate",
        examples=["sum(cycles)"]
    )
    start_date: datetime = Field(
        description="Starting date in iso format",
        examples=[datetime(year=2024,month=10,day=1)]
    )
    end_date: datetime = Field(
        description="Ending date in iso format",
        examples=[datetime(year=2024,month=10,day=30)]
    )
    unit:Units = Field(
        default=Units.DAY,
        description="the time aggregation to be used"
    )

class TimeStampResults(BaseModel):
    value:float
    time:datetime

class KPICalculationResult(BaseModel):
    start_date:datetime
    end_date:datetime
    values:Optional[float | TimeStampResults]

class CalculationKPIResponse(CalculationResponse):
    unit:str=Field(
        description="a temporal aggregation"
    )
    result:Optional[List[KPICalculationResult]]=Field(
        description="calculation result according to the specified time range and expression specified"
    )
