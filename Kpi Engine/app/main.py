from typing import Dict, List
from fastapi import Depends, FastAPI, Query, status
from fastapi.responses import JSONResponse
from Knowledge_base.knowledge_base_interface import KnowledgeBaseInterface
from KPI_engine.EngineCalculation.calculation_engine import CalculationEngine
from models import calculation_request , alert_requests
from utils.utils import calculate_segments, extract_kpi_names
from utils.calculation_utils import calculate_range_kpi,calculate_range_alert
from Alert_Monitor.alert_monitor import AlertMonitor,Alert
alert_monitor=AlertMonitor()

app = FastAPI()

"""
@file main.py
@brief Implements the main endpoints.
@ingroup api_endpoints

@include Documentation.md

This provides the main endpoints for the apis exposed to the docker.
"""
@app.on_event("startup")
def modify_openapi():
    # Access the default OpenAPI schema
    openapi_schema = app.openapi()

    # Modify the info section of the OpenAPI schema
    openapi_schema["info"]["title"] = "KPI engine"
    openapi_schema["info"]["description"] = "documentation for the kpi-engine api endpoints"
    openapi_schema["info"]["version"] = "1.0.0"  


    app.openapi_schema = openapi_schema

@app.get("/calculate/",
         summary="Calculate KPIs",
         description="Calculate KPIs for a given time range and expression",
         tags=["calculation engine"],
         response_model=calculation_request.CalculationKPIResponse,
         responses={
              200:{
                  "description":"Successful response",
                  "content":{
                      "application/json":{
                          "example":{
                                        "code": 0,
                                        "reason": "",
                                        "result": [
                                            {
                                                "start_time": "2024-03-01 00:00:00",
                                                "end_time": "2024-03-03 00:00:00",
                                                "values": 30391.0
                                            },
                                            {
                                                "start_time": "2024-03-04 00:00:00",
                                                "end_time": "2024-03-10 00:00:00",
                                                "values": 51732.0
                                            },
                                            {
                                                "start_time": "2024-03-11 00:00:00",
                                                "end_time": "2024-03-17 00:00:00",
                                                "values": 80085.0
                                            },
                                            {
                                                "start_time": "2024-03-18 00:00:00",
                                                "end_time": "2024-03-24 00:00:00",
                                                "values": 151963.0
                                            },
                                            {
                                                "start_time": "2024-03-25 00:00:00",
                                                "end_time": "2024-03-30 00:00:00",
                                                "values": 130833.0
                                            }
                                        ],
                                        "unit": "percentage",
                                        "start_time": "2024-03-01 00:00:00",
                                        "end_time": "2024-03-30 00:00:00",
                                        "expression": "sum(cycles)"
                                    }
                      }
                  }
              }
          })
def calculate(
         request: calculation_request.KPICalculationRequest = Depends()
         ):
    """
    Endpoint to calculate KPIs for a machine within a given time range and expression.
    

    Args:
        start_date: Start time.
        end_date: End time.
        machine_id: The id of the machine for which to calculate the expression.
        expression: The expression to evaluate.
    
    Returns:
        the result of the calculation along with the units and the status.
    """
    kpi_data =None
    code = calculation_request.CalculationCodes.OK
    reason = ""
    status_code=status.HTTP_200_OK
    # query validation
    if request.start_date > request.end_date:
        reason = "start time cannot be before end time\n"
        code=calculation_request.CalculationCodes.WRONG_DATA
    # semantical validity checking
    KB_kpis=KnowledgeBaseInterface.retrieve_all_kpi_data()
    kpi_names=[kpi['nameID'] for kpi in KB_kpis]
    expression_kpis=extract_kpi_names(request.expression,kpi_names)
    if not KnowledgeBaseInterface.check_kpi_availability(
        machine_id=request.machine_id,
        kpis=expression_kpis
    ):
        reason = "some kpis are not available for the request machine"
        code=calculation_request.CalculationCodes.INVALID_VALUES
    else:
        #we can actually calculate the values becasue checking went fine
        time_range=calculate_segments(request.start_date,request.end_date,request.unit)
        kpi_data=KnowledgeBaseInterface.retrieve_kpi_data(
            expression_kpis
        )
        kpi_data=[
            kpi for kpi in KB_kpis if kpi['nameID'] in expression_kpis
        ]
        # if complex kpis are present take their expression from the KB
        for kpi in kpi_data:
            if not kpi['formula'] is None:
                res=CalculationEngine.add_complex_KPI(
                    name=kpi['nameID'],
                    description=kpi['description'],
                    expression=kpi['formula'] 
                )
       
    seg_result=[]
    if calculation_request.CalculationCodes.OK == code:    
        #execute calculation
        try:
            seg_result=calculate_range_kpi(time_range,request.machine_id,request.expression,request.operation.value)
        except Exception as e:
            code=calculation_request.CalculationCodes.EXPRESSION_ERROR
            reason="calculation cannot be computed"
            seg_result=[]
    units='?'
    if kpi_data is None:
        units='?'
    #calculate the unit to return
    else:
        units=KnowledgeBaseInterface.calculate_unit(
            set( 
                map(
                    lambda kpi: kpi['unit'],
                    kpi_data
                ) 
            )
        )
    if code != calculation_request.CalculationCodes.OK:
        status_code = status.HTTP_400_BAD_REQUEST
        seg_result = []
    print("CALCULATE SEG RESULT",seg_result)
    return JSONResponse(
        content={
            "code":code.value,
            "reason":reason,
            "result":seg_result,
            "start_time":request.start_date.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time":request.end_date.strftime('%Y-%m-%d %H:%M:%S'),
            "expression":request.expression,
            "unit":units
        },
        status_code=status_code
    )


@app.get("/alert/",
         summary="Alert KPI Calculation", 
         description="Calculate an alert expression within a time range.",
         tags=["alerts"],
         response_model=alert_requests.CalculationAlertResponse,
         responses={
             200:{
                  "description":"Successful response",
                  "content":{
                      "application/json":{
                          "example":{
                                "code": 0,
                                "reason": "",
                                "result": True,
                                "start_time": "2024-03-01 00:00:00",
                                "end_time": "2024-03-30 00:00:00",
                                "expression": "sum(cycles)> 0"
                            }
                      }
                  }
              }
         })
def alert(
    request : alert_requests.KPIAlertRequest = Depends()
):  
    """
    Endpoint to calculate an alert expression based on KPI calculation within a time range.
    

    Args:
        start_date: Start date for KPI alert (ISO formatted string).
        end_date: End date for KPI alert (ISO formatted string).
        machine_id: The machine ID to check KPIs for.
        expression: The KPI expression to check against.
    
    Returns:
        the result of the alert calculation and status.
    """
    code = calculation_request.CalculationCodes.OK
    status_code = status.HTTP_200_OK
    reason = ""
    result=dict()
    #direct calculation because we don't expect wrong expressions
    try:
        result=calculate_range_alert(
            request.start_date,
            request.end_date,
            request.machine_id,
            request.expression
        )
    except Exception as e:
        code=calculation_request.CalculationCodes.EXPRESSION_ERROR
        reason="error during the calculation"
    
    if calculation_request.CalculationCodes.OK != code:
        status_code = status.HTTP_400_BAD_REQUEST
        result = None
    
    return JSONResponse(
        content={
            "code":code.value,
            "reason":reason,
            "result":result,
            "start_time":request.start_date.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time":request.end_date.strftime('%Y-%m-%d %H:%M:%S'),
            "expression":request.expression
        },
        status_code=status_code
    )

@app.post("/add_alert/",
          summary="Add a new alert", 
          description="Add a new KPI alert based on the provided parameters.",
          tags=["alerts"],
          response_model=alert_requests.AddAlertMonitorResponse,
          responses={
              200:{
                  "description":"the id of the added alert",
                  "content":{
                      "application/json":{
                          "example":{
                              "newID":"1231212"
                          }
                      }
                  }
              }
          })
def add_alert(
    request:alert_requests.AddAlertRequest
):
    """
    Endpoint to add a new alert based on a sliding time window and expression for a given machine.
    
    Args
        timeWindow: Time window for the alert in seconds.
        expression: The expression used to trigger the alert.
        machineID: The ID of the machine to monitor for KPI alert.
    
    Returns:
        the ID of the newly created alert.
    """
    #try adding the new expression to monitor
    new_id=alert_monitor.add_alert(
        Alert(
            date_range_seconds=request.sliding_window_seconds,
            expression=request.expression,
            machine_id=request.machine_id
        )
    )
    # if the epxression cannot be added notify
    if new_id == None:
        return JSONResponse(
            content="cannot calculate such expression on the reuqest machine",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return JSONResponse(
        content={
            'newID':new_id
        },
        status_code=status.HTTP_200_OK
    )
    
@app.get("/get_all_alerts/",
         summary="Get all alerts", 
         description="Retrieve a list of all active alerts.",
        tags=["alerts"],
        response_model=List[alert_requests.MonitorAlertsResponse],
        responses={
              200:{
                  "description":"the id of the added alert",
                  "content":{
                      "application/json":{
                          "example":[
                                    {
                                        "monitorUUID": "1122321",
                                        "timeWindow": 259200,
                                        "expression": "avg(good_cycles)>10000",
                                        "machineID": 2
                                    }
                                ]
                      }
                  }
              }
          })

def get_alerts():
    """
    Endpoint to retrieve all active alerts.
    
    Returns:
        a list of all active alerts in the system.
    """
    alerts=alert_monitor.get_all_alerts()
    alerts=[
        {
            'monitorUUID':alert['id'],
            'timeWindow':alert['time_window'],
            'expression':alert['expression'],
            'machineID':alert['machine']
        } for alert in alerts

    ]

    return JSONResponse(
        content=alerts,
        status_code=status.HTTP_200_OK
    )
@app.delete("/remove_alerts/",
            summary="Remove alerts", 
            description="Remove specific alerts by their IDs.",
            tags=["alerts"],
            response_model=List[Dict[str,bool]],
            responses={
                200:{
                  "description":"a list of key-value pairs where for each alert id we have true as a value if it was removed false if it wasn\'t present",
                  "content":{
                      "application/json":{
                          "example":[
                              {"123":True},
                              {"333":False}
                          ]
                      }
                  }
              }
            })
def remove_alerts(request:alert_requests.RemoveAlertsRequest):
    """
    remove alerts by their IDs.

    Args:
        alerts_ids: List of alert IDs to remove from the system.
    
    Returns:
        a list of key-value pairs where for each alert id we have true as a value if it was removed false if it wasn\'t present
    """
    remove_response=alert_monitor.remove_alerts(
        request.alerts_ids
    )
    return JSONResponse(
        content=remove_response,
        status_code=status.HTTP_200_OK
    )