from datetime import datetime, timedelta
import time
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.getcwd(), "../.."))
sys.path.append(parent_dir)
from app.Alert_Monitor.alert_monitor import AlertMonitor

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

test_alerts()