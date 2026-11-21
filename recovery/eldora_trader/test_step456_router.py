import unittest
from step456_router import plan_routes, RoutingRejected

class Tests(unittest.TestCase):
    def setUp(self):
        self.channel = {'channel_id':'a','modality':'text','size_bytes':100,'priority':5}
    def test_route(self): self.assertEqual(plan_routes('s',[self.channel])['routes'][0]['pipeline'],'nlp_core')
    def test_no_execution(self): self.assertFalse(plan_routes('s',[self.channel])['executed'])
    def test_empty_session(self):
        with self.assertRaises(RoutingRejected): plan_routes('',[self.channel])
    def test_empty_channels(self):
        with self.assertRaises(RoutingRejected): plan_routes('s',[])
    def test_duplicate(self):
        with self.assertRaises(RoutingRejected): plan_routes('s',[self.channel,self.channel])
    def test_unknown_modality(self):
        with self.assertRaises(RoutingRejected): plan_routes('s',[dict(self.channel,modality='orders')])
    def test_negative_size(self):
        with self.assertRaises(RoutingRejected): plan_routes('s',[dict(self.channel,size_bytes=-1)])
    def test_oversized(self):
        with self.assertRaises(RoutingRejected): plan_routes('s',[dict(self.channel,size_bytes=100_000_001)])
    def test_boolean_size(self):
        with self.assertRaises(RoutingRejected): plan_routes('s',[dict(self.channel,size_bytes=True)])
    def test_priority(self):
        with self.assertRaises(RoutingRejected): plan_routes('s',[dict(self.channel,priority=11)])
    def test_channel_limit(self):
        with self.assertRaises(RoutingRejected): plan_routes('s',[dict(self.channel,channel_id=str(i)) for i in range(101)])
    def test_all_modalities(self):
        channels=[dict(self.channel,channel_id=str(i),modality=m) for i,m in enumerate(('text','audio','video','three_d'))]
        self.assertEqual(len(plan_routes('s',channels)['routes']),4)
if __name__ == '__main__': unittest.main()
