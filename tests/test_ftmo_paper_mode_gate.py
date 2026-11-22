import unittest
from app.runtime.ftmo_paper_mode_gate import dispatch_simulated_intent, ExecutionModeBlocked

class ModeGateTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.engine = lambda intent: self.calls.append(intent) or {'status':'paper_recorded'}
    def intent(self, mode='PAPER'):
        return {'mode':mode,'live':False,'real_orders':False,'symbol':'EURUSD'}
    def test_paper(self):
        self.assertEqual(dispatch_simulated_intent('PAPER',self.intent(),self.engine)['status'],'paper_recorded')
        self.assertEqual(len(self.calls),1)
    def test_demo(self):
        self.assertEqual(dispatch_simulated_intent('DEMO',self.intent('DEMO'),self.engine)['status'],'paper_recorded')
    def test_forbidden_modes_never_call_engine(self):
        for mode in ('LIVE','REAL','FTMO_REAL','paper','',None,0,True,'PAPER '):
            with self.subTest(mode=mode):
                with self.assertRaises(ExecutionModeBlocked):
                    dispatch_simulated_intent(mode,self.intent(),self.engine)
        self.assertEqual(self.calls,[])
    def test_mode_mismatch_never_calls_engine(self):
        with self.assertRaises(ExecutionModeBlocked):
            dispatch_simulated_intent('PAPER',self.intent('DEMO'),self.engine)
        self.assertEqual(self.calls,[])
    def test_live_flag_never_calls_engine(self):
        for key in ('live','real_orders'):
            intent=self.intent()
            intent[key]=True
            with self.assertRaises(ExecutionModeBlocked):
                dispatch_simulated_intent('PAPER',intent,self.engine)
        self.assertEqual(self.calls,[])
    def test_missing_false_flags_rejected(self):
        for key in ('live','real_orders'):
            intent=self.intent()
            del intent[key]
            with self.assertRaises(ExecutionModeBlocked):
                dispatch_simulated_intent('PAPER',intent,self.engine)
        self.assertEqual(self.calls,[])
    def test_invalid_engine_rejected(self):
        with self.assertRaises(ExecutionModeBlocked):
            dispatch_simulated_intent('PAPER',self.intent(),None)
    def test_invalid_intent_rejected(self):
        for intent in ({},None,[],0):
            with self.assertRaises(ExecutionModeBlocked):
                dispatch_simulated_intent('PAPER',intent,self.engine)
        self.assertEqual(self.calls,[])
