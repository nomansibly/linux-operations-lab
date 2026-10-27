import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from health_monitor import cpu_percent, alerts
class MetricsTests(unittest.TestCase):
    def test_cpu_delta(self): self.assertEqual(cpu_percent((100,40),(200,60)),80)
    def test_no_elapsed_ticks(self): self.assertIsNone(cpu_percent((100,40),(100,40)))
    def test_unknown_not_healthy(self): self.assertEqual(alerts(None,10,10,None),['cpu_unknown','service_unhealthy'])
    def test_threshold(self): self.assertEqual(alerts(85,84.9,85,200),['cpu_high','disk_high'])
if __name__=='__main__': unittest.main()
