import unittest
from p2395_context_router_safe import build_router
EDGE = {'decision':'OBSERVE_SCORE','final_score':68.391266,'key':'edge1','direction':'LONG'}
CTX = {'key':'edge1','direction':'LONG','mode':'PAPER_ONLY','real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN'}
class RouterTests(unittest.TestCase):
    def test_observe(self):
        result=build_router(EDGE).route(CTX)
        self.assertEqual(result.route,'OBSERVE_ONLY')
        self.assertFalse(result.allowed)
    def test_context_missing(self):
        self.assertEqual(build_router(EDGE).route({}).route,'BLOCK')
    def test_context_mismatch(self):
        self.assertEqual(build_router(EDGE).route({**CTX,'key':'other'}).route,'BLOCK')
    def test_unsafe_mode(self):
        self.assertEqual(build_router(EDGE).route({**CTX,'mode':'LIVE'}).route,'BLOCK')
    def test_promoted_claim(self):
        self.assertEqual(build_router({**EDGE,'decision':'PROMOTE_SCORE'}).route(CTX).route,'BLOCK')
    def test_bad_score(self):
        self.assertEqual(build_router({**EDGE,'final_score':float('nan')}).route(CTX).route,'BLOCK')
    def test_extra_flag(self):
        self.assertEqual(build_router(EDGE).route({**CTX,'order_dispatch':True}).route,'BLOCK')
if __name__=='__main__': unittest.main()
