"""Offline regressions for the original P2223 simulation-only broker emulator."""
import unittest
from app.runtime.p2223_broker_emulator import BrokerEmulator, run_simulation

class BrokerEmulatorSafetyTests(unittest.TestCase):
    def test_invalid_side_rejected_without_market_mutation(self):
        broker=BrokerEmulator()
        price=broker.market.price
        with self.assertRaisesRegex(ValueError,'side'):
            broker.execute_order('HOLD',1)
        self.assertEqual(broker.market.price,price)
        self.assertEqual(broker.trades,[])
    def test_invalid_volume_rejected_without_market_mutation(self):
        for volume in (0,-1,True,1.5,'1',None):
            with self.subTest(volume=volume):
                broker=BrokerEmulator()
                with self.assertRaisesRegex(ValueError,'volume'):
                    broker.execute_order('BUY',volume)
                self.assertEqual(broker.market.price,100.0)
                self.assertEqual(broker.trades,[])
    def test_pre_halted_risk_rejects_before_market_tick(self):
        broker=BrokerEmulator()
        broker.risk.equity=90000
        with self.assertRaisesRegex(RuntimeError,'halted'):
            broker.execute_order('SELL',1)
        self.assertEqual(broker.market.price,100.0)
        self.assertEqual(broker.trades,[])
    def test_valid_paper_order_stays_simulated(self):
        broker=BrokerEmulator()
        trade=broker.execute_order('BUY',1)
        self.assertEqual(trade['side'],'BUY')
        self.assertEqual(len(broker.trades),1)
    def test_risk_kill_latches_and_blocks_future_orders(self):
        broker=BrokerEmulator()
        self.assertEqual(broker.risk.check(-6000),'KILLED')
        self.assertTrue(broker.risk.halted)
        broker.risk.equity=broker.risk.peak
        with self.assertRaisesRegex(RuntimeError,'halted'):
            broker.execute_order('BUY',1)
        self.assertEqual(broker.trades,[])
    def test_zero_peak_rejected_before_division(self):
        broker=BrokerEmulator()
        broker.risk.peak=0
        with self.assertRaisesRegex(RuntimeError,'halted'):
            broker.execute_order('BUY',1)
        self.assertEqual(broker.trades,[])
    def test_session_loss_limit_enforced_before_drawdown_limit(self):
        broker=BrokerEmulator()
        self.assertEqual(broker.risk.check(-3100),'KILLED')
        self.assertTrue(broker.risk.halted)
        self.assertLess((broker.risk.peak-broker.risk.equity)/broker.risk.peak,broker.risk.max_drawdown)
        with self.assertRaisesRegex(RuntimeError,'halted'):
            broker.execute_order('BUY',1)
        self.assertEqual(broker.trades,[])
    def test_killed_risk_cannot_mutate_equity(self):
        broker=BrokerEmulator()
        broker.risk.check(-3100)
        equity=broker.risk.equity
        with self.assertRaisesRegex(RuntimeError,'halted'):
            broker.risk.check(99999)
        self.assertEqual(broker.risk.equity,equity)
    def test_nonfinite_pnl_rejected_without_mutation(self):
        for pnl in (float('nan'),float('inf'),float('-inf'),True,'100'):
            with self.subTest(pnl=pnl):
                broker=BrokerEmulator()
                with self.assertRaises(ValueError):
                    broker.risk.check(pnl)
                self.assertEqual(broker.risk.equity,100000)
    def test_preexisting_session_loss_blocks_order(self):
        broker=BrokerEmulator()
        broker.risk.equity=96000
        broker.risk.peak=100000
        with self.assertRaisesRegex(RuntimeError,'halted'):
            broker.execute_order('BUY',1)
        self.assertEqual(broker.trades,[])
    def test_simulation_rejects_invalid_cycles(self):
        for cycles in (True, 1.5, '10', None):
            with self.subTest(cycles=cycles), self.assertRaises(TypeError):
                run_simulation(cycles)
        for cycles in (-1, 0, 10001):
            with self.subTest(cycles=cycles), self.assertRaises(ValueError):
                run_simulation(cycles)
    def test_simulation_one_cycle(self):
        result=run_simulation(1)
        self.assertEqual(result['total_trades'],1)
        self.assertEqual(result['mode'],'BROKER_EMULATOR_SIMULATION_ONLY')
if __name__=='__main__':unittest.main()
