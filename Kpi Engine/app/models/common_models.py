from typing import  List, Optional
from enum import Enum
from pydantic import BaseModel,Field
from datetime import datetime
class BASEKPINames(Enum):
    WORKING_TIME = "working_time"
    IDLE_TIME = "idle_time"
    OFFLINE_TIME = "offline_time"
    CONSUMPTION = "consumption"
    POWER = "power"
    COST = "cost"
    CONSUMPTION_WORKING = "consumption_working"
    CONSUMPTION_idle = "consumption_idle"
    CYCLES = "cycles"
    BAD_CYCLES = "bad_cycles"
    GOOF_CYCLES = "good_cycles"
    AVERAGE_CYCLE_TIME = "average_cycle_time"

class CalculationCodes(Enum):
    OK = 0
    INVALID_VALUES = 1
    EXPRESSION_ERROR = 2
    WRONG_DATA = 3
    GENERIC_ERROR = 4

class AggregationOperation(Enum):
    SUM = 'sum'
    AVG = 'avg'
    MIN = 'min'
    MAX = 'max'

class Units(Enum):
    NONE = '-'
    DAY = 'd'
    WEEK = 'w'
    MONTH = 'm'
    YEAR = 'y'


class CalculationResponse(BaseModel):
    code:CalculationCodes=Field(
        description="a code describing what happened fore the requested calculation"
    )
    reason:str=Field(
        description="a textual explanation of the code meaning,mioght change depending on the sitaution"
    )
    result:any=Field(
        description="calculation result,depends on the endpoint"
    )
    start_time:datetime=Field(
        description="start of time range for the calculation",
    )
    end_time:datetime=Field(
        description="end of time range for the calculation",
        default=datetime.now()
    )
    expression:str=Field(
        description="the expression to be calculated"
    )