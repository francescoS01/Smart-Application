import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import unittest
from Alert_Monitor.alert_monitor import AlertMonitor, Alert
from datetime import timedelta

class TestAlertMonitor(unittest.TestCase):

    def test_add_alerts(self):
        
        alert_monitor = AlertMonitor()
        
        alert_id1 = alert_monitor.add_alert(Alert(timedelta(days = 3).total_seconds(), "avg(cycles)", 3))
        self.assertEqual(alert_monitor.get_all_alerts([alert_id1])[0]['monitorUUID'], alert_id1)
        
        alert_id2 = alert_monitor.add_alert(Alert(timedelta(days = 3).total_seconds(), "avg(cycles)", 3))
        self.assertEqual(alert_monitor.get_all_alerts([alert_id2])[1]['monitorUUID'], alert_id2)
        
        self.assertNotEqual(alert_id1, alert_id2)

        alert_monitor._reset()

    def test_multiple_adds(self):
        
        alert_monitor = AlertMonitor()
        
        ids_to_check = [
            alert_monitor.add_alert(Alert(timedelta(days = 3).total_seconds(), "avg(cycles)", 3)),
            alert_monitor.add_alert(Alert(timedelta(days = 3).total_seconds(), "sum(cycles)", 7)),
            alert_monitor.add_alert(Alert(timedelta(days = 3).total_seconds(), "max(cycles)", 9))
        ]
        
        retrieved_ids = list(map(lambda data: data['monitorUUID'], alert_monitor.get_all_alerts()))

        for id in ids_to_check: self.assertIn(id, retrieved_ids)

        self.assertDictEqual(alert_monitor.remove_alerts([ids_to_check[0]]), {ids_to_check[0]:True})
        self.assertDictEqual(alert_monitor.remove_alerts([ids_to_check[0]]), {ids_to_check[0]:False})
        
        self.assertNotIn(ids_to_check[0], list(map(lambda data: data['monitorUUID'], alert_monitor.get_all_alerts())))
        
        alert_monitor._reset()

    def test_add_and_retrieve_alerts(self):
        
        alert_monitor = AlertMonitor()
        
        ids_to_check = [
            alert_monitor.add_alert(Alert(timedelta(days = 3).total_seconds(), "avg(cycles)", 3)),
            alert_monitor.add_alert(Alert(timedelta(days = 6).total_seconds(), "sum(cycles)", 7)),
            alert_monitor.add_alert(Alert(timedelta(days = 3).total_seconds(), "max(cycles)", 9))
        ]

        retrieved_ids = list(map(lambda data: data['id'], alert_monitor.get_all_alerts()))

        for id in ids_to_check: self.assertIn(id, retrieved_ids)
        alert_monitor._reset()


if __name__ == '__main__':
    unittest.main()