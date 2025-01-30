from locust import HttpUser, task, constant
import random

class KPIEngineUser(HttpUser):
    wait_time = constant(0)  # Attesa nulla tra un task ed un altro
    
    @task
    def add_alert(self):
        
        self.client.post("/add_alert/", json = {
            "expression": "sum(cycles)>50",
            "machine_id": 2,
            "sliding_window_seconds": 10000
            })
        
    @task
    def get_all_alerts(self):
        self.client.get("/get_all_alerts/")
        
    @task
    def remove_alerts(self):
        self.client.delete("/remove_alerts/", json={"alerts_ids": []})
    
    @task
    def calculate(self):
        self.client.get("/calculate/", params = {"machine_id": 2,
                                                 "operation": "sum",
                                                 "expression": "cycles",
                                                 "start_date": "2024-03-01 00:00:00",
                                                 "end_date": "2024-03-22 00:00:00",
                                                 "unit": "d"})