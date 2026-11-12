import csv
import json
import unittest
from pathlib import Path
from tests.test_et665_m8_gateway_e2e import M8GatewayE2E
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.backtest.p2405_historical_exit import select_historical_exit
from mind_trader.app.backtest.p2405_paper_gateway import replay_candidate_to_paper
from mind_trader.app.backtest.p2405_paper_settlement import settle_selected_historical_exit
from mind_trader.app.execution.paper_session import PaperTradingSessionManager


class M10HistoricalExits(unittest.TestCase):
    def setUp(self):
        M8GatewayE2E.setUp(self)
        self.db=self.root/"exits.sqlite"
        self.entry_ts=self.candidate["fill_ts"]

    def history(self,side,stop,target,first,second=None):
        # Real first entry timestamp, then future candles. No lookahead.
        candles=[(self.entry_ts,100,101,99,100),
                 ("2026-01-02T00:00:00",*first)]
        if second:
            candles.append(("2026-01-02T00:01:00",*second))
        path=self.root/"exit_bars.csv"
        with path.open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=["ts","open","high","low","close","volume"])
            writer.writeheader()
            for ts,op,hi,lo,cl in candles:
                writer.writerow(dict(ts=ts,open=op,high=hi,low=lo,close=cl,volume=1))
        ingest_ohlcv_csv(str(path),"EURUSD","M1",str(self.db))
        return select_historical_exit("EURUSD","M1",str(self.db),fill_ts=self.entry_ts,
                                      side=side,stop=stop,target=target)

    def test_buy_stop_precedes_target_in_same_bar(self):
        x=self.history("BUY",99,102,(100,103,98,101))
        self.assertEqual((x["exit_reason"],x["exit_close"]),("STOP",99))

    def test_sell_stop_precedes_target_in_same_bar(self):
        x=self.history("SELL",102,98,(100,103,97,99))
        self.assertEqual((x["exit_reason"],x["exit_close"]),("STOP",102))

    def test_buy_gap_uses_open(self):
        x=self.history("BUY",99,102,(96,97,95,96))
        self.assertEqual((x["exit_reason"],x["exit_close"]),("STOP_GAP",96))

    def test_sell_gap_uses_open(self):
        x=self.history("SELL",102,98,(105,106,104,105))
        self.assertEqual((x["exit_reason"],x["exit_close"]),("STOP_GAP",105))

    def test_no_future_exit_blocks(self):
        x=self.history("BUY",99,102,(100,101,99.5,100))
        self.assertEqual(x["decision"],"BLOCK_NO_HISTORICAL_EXIT")

    def test_gateway_entry_friction_once_and_candidate_integrity(self):
        accepted=replay_candidate_to_paper(self.candidate,self.gateway,risk_amount=10,
            stop_distance=1,reward_multiple=2.5,regime_report=self.regime,
            genome=self.genome,authorize_offline_replay=True)
        self.assertEqual(accepted["decision"],"ACCEPT_SIMULATED_ORDER",accepted)
        rows=[json.loads(x) for x in self.broker.read_text().splitlines()]
        fill=rows[-1]["fill"]["fill_price"]
        self.assertAlmostEqual(fill,self.candidate["simulated_fill"])
        tampered=dict(self.candidate,simulated_fill=self.candidate["simulated_fill"]+1)
        rejected=replay_candidate_to_paper(tampered,self.gateway,risk_amount=10,
            stop_distance=1,reward_multiple=2.5,regime_report=self.regime,
            genome=self.genome,authorize_offline_replay=True)
        self.assertEqual(rejected["reason"],"CANDIDATE_INTEGRITY_MISMATCH")

    def test_buy_net_pnl_and_recovery(self):
        accepted=replay_candidate_to_paper(self.candidate,self.gateway,risk_amount=10,
            stop_distance=1,reward_multiple=2.5,regime_report=self.regime,
            genome=self.genome,authorize_offline_replay=True)
        self.assertEqual(accepted["decision"],"ACCEPT_SIMULATED_ORDER",accepted)
        rows=[json.loads(x) for x in self.broker.read_text().splitlines()]
        order=rows[-1]["order"]
        price=order["entry"]
        self.history("BUY",order["stop"],order["target"],
                     (price,price+3,price-0.2,price+2.8))
        restarted=PaperTradingSessionManager(str(self.session),str(self.day),str(self.config))
        result=settle_selected_historical_exit(restarted,broker_ledger_path=str(self.broker),
            reservation_id=accepted["reservation_id"],symbol="EURUSD",timeframe="M1",
            db_path=str(self.db),entry_ts=self.entry_ts,quantity=2,
            quote_to_account_rate=1,settlement_evidence_path=self.root/"m10.json",
            authorize_offline_replay=True)
        self.assertEqual(result["decision"],"M9_HISTORICAL_PAPER_SETTLED",result)
        self.assertEqual(result["exit_reason"],"TARGET")
        self.assertAlmostEqual(result["net_account"],(result["exit_fill"]-result["entry_fill"])*2-2)
        self.assertEqual(json.loads(self.session.read_text())["trades"],1)
        again=settle_selected_historical_exit(restarted,broker_ledger_path=str(self.broker),
            reservation_id=accepted["reservation_id"],symbol="EURUSD",timeframe="M1",
            db_path=str(self.db),entry_ts=self.entry_ts,quantity=2,
            quote_to_account_rate=1,settlement_evidence_path=self.root/"m10.json",
            authorize_offline_replay=True)
        self.assertNotEqual(again["decision"],"M9_HISTORICAL_PAPER_SETTLED")
        self.assertEqual(json.loads(self.session.read_text())["trades"],1)


    def test_sell_net_pnl(self):
        self.candidate=next(e for e in self.research["events"] if e["side"]=="SELL")
        self.entry_ts=self.candidate["fill_ts"]
        accepted=replay_candidate_to_paper(self.candidate,self.gateway,risk_amount=10,
            stop_distance=1,reward_multiple=2.5,regime_report=self.regime,
            genome=self.genome,authorize_offline_replay=True)
        self.assertEqual(accepted["decision"],"ACCEPT_SIMULATED_ORDER",accepted)
        row=json.loads(self.broker.read_text().splitlines()[-1])
        order=row["order"]
        price=order["entry"]
        self.history("SELL",order["stop"],order["target"],
                     (price,price+0.2,price-3,price-2.8))
        restarted=PaperTradingSessionManager(str(self.session),str(self.day),str(self.config))
        result=settle_selected_historical_exit(restarted,broker_ledger_path=str(self.broker),
            reservation_id=accepted["reservation_id"],symbol="EURUSD",timeframe="M1",
            db_path=str(self.db),entry_ts=self.entry_ts,quantity=2,
            quote_to_account_rate=1,settlement_evidence_path=self.root/"sell.json",
            authorize_offline_replay=True)
        self.assertEqual(result["decision"],"M9_HISTORICAL_PAPER_SETTLED",result)
        self.assertEqual(result["exit_reason"],"TARGET")
        self.assertAlmostEqual(result["net_account"],(result["entry_fill"]-result["exit_fill"])*2-2)


if __name__=="__main__":
    unittest.main()
