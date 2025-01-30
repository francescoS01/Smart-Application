from locust import HttpUser, task, between

#Calculate
#AddAlert    #Da fare ancora
#RemoveAlert #Da fare ancora
#Alerts

class KPIEngineUser(HttpUser):
    wait_time = between(1, 3)  # Attesa casuale tra le richieste

    @task
    def get_metrics(self):
        self.client.get("/alerts/")  # Sostituisci con un endpoint valido

    @task
    def calculate_kpi(self):
        pass
        #self.client.post("/api/calculate", json={"data": "example"})  # Sostituisci con un'API POST