import sys
import os

parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(parent_dir)
parent_dir = os.path.abspath(os.path.join(os.getcwd(), "../.."))
sys.path.append(parent_dir)

from datetime import datetime, timedelta
import requests
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
import logging
import uuid
from apscheduler.triggers.cron import CronTrigger

from models.calculation_request import BASEKPINames
from typing import Dict,List
from Knowledge_base.knowledge_base_interface import KnowledgeBaseInterface
from utils.utils import get_token, BASE_URL ,AUTH_URL ,YOUR_PASSWORD ,YOUR_USERNAME,extract_kpi_names

        


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()


def fire_alert(machine_id:int,kpis:List[str],expression:str,time_range:float)->None:
    """
    notify the alert to the api layer

    Args:
        machine_id: the id of the machine
        kpis: the kpis involved
        expression: the expression calculated
        time_range: the sliding window time range
    """
    ALERT_URL=f'{BASE_URL}/alert'
    token=get_token(AUTH_URL,YOUR_USERNAME,YOUR_PASSWORD)

    for kpi in kpis:
        result=requests.post(
            ALERT_URL,
            headers={
                    'timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'machineID':str(machine_id),
                    'severity':'medium',
                    'description':f'fired from alert monitor with expression {expression} with time range {time_range}',
                    'KPI':kpi,
                    'Authorization':token
                },
            verify=False
        )
        logger.info("alert result",result.json())

class Alert:
    def __init__(
        self,
        date_range_seconds:float,
        expression:str,
        machine_id:int
    ):
        self.date_range:float=date_range_seconds
        self.expression:str=expression
        self.machine_id:int=machine_id

class AlertMonitor():
    __instance=None
    def __new__(cls):
        if cls.__instance is None:
            logger.info("initializing the alert monitor")

            cls.__instance = super(AlertMonitor, cls).__new__(cls)

            cls.__url:str="http://localhost:8000/alert/"
            cls.__scheduler = BackgroundScheduler()
            
            cls.__instance.load_config()
            cls.__instance.start()
        return cls.__instance
    def add_alert(self,alert:Alert) -> str:
        """
        add a new alert to be monitored
        """

        KB_kpis=[kpi.value for kpi in BASEKPINames]
        expression_kpis=extract_kpi_names(alert.expression,KB_kpis)
        if not KnowledgeBaseInterface.check_kpi_availability(alert.machine_id,expression_kpis):
            return None
        new_id=str(uuid.uuid4())
        self.__scheduler.add_job(
                self._make_alert_request,
                args=[
                    alert.date_range,
                    alert.expression,
                    alert.machine_id
                ],
                id=new_id,
                trigger=CronTrigger(hour="0-23/2", minute=0) 
            )
        return new_id
    
    def load_config(self) -> None:
        #for now the base config is enough
        pass
    def start(self) -> None:
        """
        start the engine
        """
        self.__scheduler.start()
    def get_all_alerts(self,alert_ids:list[str]=[])->List[Dict]:
        """
        retrieve all stored alerts


        Args:
            alert_ids: contains the ids to remove

        Returns:
            a list containing all the laerts stored
        """
        # retrieve jobs
        jobs_data=list(map(
            lambda x:{
                "id":x.id,
                "time_window":x.args[0],
                "expression":x.args[1],
                "machine":x.args[2],
            },
            self.__scheduler.get_jobs()
        ))
        #filter jobs if ids are specified
        if len(alert_ids) !=0:
            jobs_data=list(filter(lambda job: job['id'] in alert_ids,jobs_data))
        return jobs_data
    def remove_alerts(self,alerts_ids:List[str]=[])->List[Dict[str,bool]]:
        """
        remove all specified alerts

        Args:
            alert_ids: contains the ids to remove

        Returns:
            a list of key value pairs each one, for each key we have true if it was removed or false if it wasn't
        """
        response=dict()
        if alerts_ids==None or len(alerts_ids)== 0:
            return response
        
        for id in alerts_ids:
            try:
                self.__scheduler.remove_job(job_id=id)
                response[id]=True
            # failsafe for unseen cases
            except JobLookupError as jle:
                response[id]=False
        return response

    def _make_alert_request(self,date_range:float,expression:str,machine_id:int,starting_date:datetime=datetime.now())->None:
        """
        make an alert calculation request to the kpi engine

        Args:
            date_range: how far back in time the sliding window should go, specified in seconds
            expression: the expression to calculate
            machine_id: on which machine it should be calculated
            starting_date: from which point in time the sliding window should start
        """
        KB_kpis=[kpi.value for kpi in BASEKPINames]
        expression_kpis=extract_kpi_names(expression,KB_kpis)






        #calculate the time-frame where the expression is calculated
        start_date=starting_date-timedelta(seconds=date_range)
        end_date=starting_date

        # make the alert request
        params={
            'machine_id':machine_id,
            'expression':expression,
            'start_date':start_date.strftime("%Y-%m-%dT%H:%M:%S"),
            'end_date':end_date.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        response=requests.get(url=self.__url,params=params, verify=False).json()

        #retrieve result and fire it if necessary
        send_alert=response['result']
        logger.info(f"""date:{start_date}
                    {'alert detected' if send_alert else 'no alert detected'}
                    expression:{expression}
                    time window:{date_range}"""
                )
        if send_alert:
            fire_alert( 
                machine_id,
                expression_kpis,
                expression,
                date_range
            )
    def _reset(self):
        self.__instance=None

def test_alerts():
    interval= 2
    counter=0
    while True and counter<20:
        time.sleep(interval)
        AlertMonitor()._make_alert_request(
            starting_date= datetime(year=2024,month=10,day=3+counter),
            date_range=timedelta(days=3).total_seconds(),
            expression="avg(good_cycles)>10000",
            machine_id=2
        )
        counter+=1
        
# adding an alert
AlertMonitor().add_alert(
    Alert(
        60*60*24*3,
        "avg(good_cycles)>10000",
        2
    )
)