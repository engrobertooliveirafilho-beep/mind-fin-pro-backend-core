import unittest
from app.cognition.strategic_summary_step448.engine import StrategicPoint,SummaryRequest,run_strategic_summary
class Step448Tests(unittest.TestCase):
    def test_duplicate_equal_points_not_both_included(self):
        p=StrategicPoint(text='same',weight=.5)
        r=run_strategic_summary(SummaryRequest(topic='paper',points=[p,p.model_copy()],max_items=1))
        self.assertEqual(sum(x.included for x in r.items),1)
    def test_missing_tag_does_not_fallback(self):
        r=run_strategic_summary(SummaryRequest(topic='paper',points=[StrategicPoint(text='risk',tag='risk')],focus_tags=['finance']))
        self.assertEqual(r.stats['points_considered'],0)
        self.assertEqual(r.items,[])
    def test_sort(self):
        r=run_strategic_summary(SummaryRequest(topic='paper',points=[StrategicPoint(text='low',weight=.1),StrategicPoint(text='high',weight=.9)],max_items=1))
        self.assertEqual(r.items[0].text,'high')
    def test_utc(self):
        r=run_strategic_summary(SummaryRequest(topic='paper',points=[]))
        self.assertTrue(r.meta['created_at'].endswith('Z'))
