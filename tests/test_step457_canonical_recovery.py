import unittest
from app.step457_gpu_autoscaling.engine import get_gpu_status,run_autoscale
class Step457RecoveryTests(unittest.TestCase):
    def test_offline_status(self):
        self.assertEqual(get_gpu_status(),{'status':'offline_simulation','gpu_provisioned':False,'cost_brl':0})
    def test_idle_no_instances(self):
        self.assertEqual(run_autoscale()['desired_instances'],0)
    def test_pressure_is_only_proposal(self):
        result=run_autoscale(queue_length=100,avg_latency_ms=4000,current_instances=0)
        self.assertGreater(result['desired_instances'],0)
        self.assertFalse(result['gpu_provisioned'])
        self.assertEqual(result['cost_brl'],0)
    def test_bounded_capacity(self):
        result=run_autoscale(queue_length=10000,avg_latency_ms=4000,current_instances=2,max_instances=4)
        self.assertLessEqual(result['desired_instances'],4)
    def test_invalid_numeric_rejected(self):
        with self.assertRaises((ValueError,TypeError,OverflowError)):
            run_autoscale(queue_length='not-a-number')
    def test_nan_rejected(self):
        with self.assertRaises(ValueError):run_autoscale(avg_latency_ms=float('nan'))
    def test_inf_rejected(self):
        with self.assertRaises(ValueError):run_autoscale(target_latency_ms=float('inf'))
    def test_inverted_capacity_rejected(self):
        with self.assertRaises(ValueError):run_autoscale(min_instances=5,max_instances=2)
    def test_zero_max_capacity_respected(self):
        with self.assertRaises(ValueError):run_autoscale(max_instances=0)
    def test_unknown_parameter_rejected(self):
        with self.assertRaises(ValueError):run_autoscale(provision_gpu=True)
if __name__=='__main__':unittest.main()

