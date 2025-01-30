import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from main import app

client = TestClient(app)

class TestApi(unittest.TestCase):
    
    def test_calculate_api(self):
        
        client = TestClient(app)

        response = client.get("/calculate/", params = {
            "machine_id": 0,
            "expression": "(good_cycles/cycles)",
            "start_date": "2024-10-14",
            "end_date": "2024-10-19"})

        self.assertEqual(response.status_code, 200)
    
    def test_add_alert_api(self):
        
        client = TestClient(app)
        
        response = client.post("/add_alert/", json = {
            'sliding_window_seconds': 2.0,
            'expression':'avg(cycles)',
            'machine_id': 0
        })
        
        self.assertEqual(list(response.json().keys()), ["new_id"])
        
        response1 = client.post("/add_alert/", json = {
            'sliding_window_seconds': 2.0,
            'expression':'avg(cycles)',
            'machine_id': 0
        })
        
        response2 = client.post("/add_alert/", json = {
            'sliding_window_seconds': 2.0,
            'expression':'min(cycles)',
            'machine_id': 0
        })
        print("RESPONSES",response1,response2)
        id1 = response1.json()["new_id"]
        id2 = response2.json()["new_id"]
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        self.assertNotEqual(id1, id2)
    
    def test_get_all_alerts_api(self):
        
        client = TestClient(app)
        
        
        id1 = client.post("/add_alert/", json = {
            'sliding_window_seconds': 2.0,
            'expression':'min(cycles)',
            'machine_id': 0
        }).json()["new_id"]
        
        response1 = client.get("/get_all_alerts/")
        
        print(response1.json())
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(len(response1.json()), 1)
        self.assertEqual(response1.json()[0]["timeWindow"], 2)
        self.assertEqual(response1.json()[0]["expression"], "min(cycles)")
        self.assertEqual(response1.json()[0]["machineID"], 0)
        self.assertEqual(response1.json()[0][""], id1)
        
        id2 = client.post("/add_alert/", json = {
            'sliding_window_seconds': 4.0,
            'expression':'avg(cycles)',
            'machine_id': 2
        }).json()["new_id"]
        
        response2 = client.get("/get_all_alerts/")
        
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(response2.json()), 2)
        
        self.assertEqual(response2.json()[0]["timeWindow"], 2)
        self.assertEqual(response2.json()[0]["expression"], "min(cycles)")
        self.assertEqual(response2.json()[0]["machineID"], 0)
        self.assertEqual(response2.json()[0][""], id1)
        
        self.assertEqual(response2.json()[1]["timeWindow"], 4)
        self.assertEqual(response2.json()[1]["expression"], "avg(cycles)")
        self.assertEqual(response2.json()[1]["machineID"], 2)
        self.assertEqual(response2.json()[1][""], id2)
        
        client.delete("/remove_alerts/", params = {'alerts_ids': [id1]})
        response3 = client.get("/get_all_alerts/")
        
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(len(response3.json()), 1)
        
        self.assertEqual(response3.json()[0]["timeWindow"], 4)
        self.assertEqual(response3.json()[0]["expression"], "avg(cycles)")
        self.assertEqual(response3.json()[0]["machineID"], 2)
        self.assertEqual(response3.json()[0][""], id2)
    
    def test_remove_alerts_api(self):
        
        client = TestClient(app)
        
        add_response = client.post("/add_alert/", json = {
            'sliding_window_seconds': 2.0,
            'expression':'avg(cycles)',
            'machine_id': 0
        })
        
        id = add_response.json()["new_id"]
        
        delete_response = client.delete("/remove_alerts/", params = {'alerts_ids': []})
        
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.json(), {})
        
        delete_response = client.delete("/remove_alerts/", params = {'alerts_ids': [id, "ss"]})
        
        self.assertEqual(delete_response.status_code, 200)
        self.assertTrue(delete_response.json()[id])
        self.assertFalse(delete_response.json()["ss"])
        
        delete_response = client.delete("/remove_alerts/", params = {'alerts_ids': [id, "ss"]})
        
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(delete_response.json()[id])
        self.assertFalse(delete_response.json()["ss"])

if __name__ == "__main__":
    unittest.main()