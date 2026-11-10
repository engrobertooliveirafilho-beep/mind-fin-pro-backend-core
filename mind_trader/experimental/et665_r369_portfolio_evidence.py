"""ET665.R369: deterministic portfolio evidence with per-strategy provenance.

Synthetic fixtures only. This is NOT historical P2405 integration, nor
an official Phase B or HP19 certification.
"""
import argparse,hashlib,json
from pathlib import Path
from mind_trader.experimental.et665_r368_portfolio_backtest import portfolio
from app.agents._et665_r356_common import digest

def build():
    rows={}
    for name,sign in (("trend",1),("countertrend",-1),("flat",0)):
        rows[name]=[{"ts":i,"open":str(100+i),"close":str(101+i),
                     "signal":sign if i%3 else 0} for i in range(10)]
    weights={"trend":"0.5","countertrend":"0.3","flat":"0.2"}
    result=portfolio(rows,weights,spread_bps="5",slippage_bps="3",commission_bps="2")
    evidence={"schema":"ET665.R369.v1","source":"SYNTHETIC_FIXTURE_NOT_P2405",
              "strategy_count":len(rows),"weights":weights,
              "input_sha256":digest(rows),"inputs":rows,
              "result":result,"official_hp19_certified":False,
              "phase_b_certified":False,"historical_p2405_integrated":False}
    evidence["evidence_sha256"]=digest(evidence)
    return evidence

def main():
    p=argparse.ArgumentParser();p.add_argument("--output",required=True);a=p.parse_args()
    data=build();path=Path(a.output)
    path.write_text(json.dumps(data,sort_keys=True,indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps({"status":"SYNTHETIC_PORTFOLIO_PASS","strategies":data["strategy_count"],
                      "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                      "historical_p2405_integrated":False}))
if __name__=="__main__":main()
