import json
from pathlib import Path
from datetime import datetime, UTC
import MetaTrader5 as mt5

OUT=Path('reports/P79_DEMO_ORDER_AUDIT_POSITION_MONITOR')

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    for name in ('p79_positions.json','p79_report.json'):
        (OUT/name).unlink(missing_ok=True)
    if not mt5.initialize():
        raise RuntimeError('MT5 initialization failed')
    try:
        account=mt5.account_info()
        terminal=mt5.terminal_info()
        if account is None or terminal is None or not terminal.connected:
            raise RuntimeError('MT5 connection unavailable')
        if account.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
            raise RuntimeError('Non-demo account forbidden')
        positions=mt5.positions_get()
        if positions is None:
            raise RuntimeError('MT5 positions query failed')
        data=[p._asdict() for p in positions]
        report=dict(STATUS='P79_DEMO_ORDER_AUDIT_POSITION_MONITOR_COMPLETED',ACCOUNT_LOGIN=account.login,ACCOUNT_SERVER=account.server,TERMINAL_CONNECTED=terminal.connected,TERMINAL_TRADE_ALLOWED=terminal.trade_allowed,POSITIONS_TOTAL=len(data),POSITIONS=data,ORDER_SENT=False,NEW_ORDER_SENT=False,MONITOR_ONLY=True,NEXT='P80_DEMO_POSITION_RISK_MONITOR_AND_EXIT_GOVERNOR',LIVE='FORBIDDEN',REAL_BROKER='DISABLED',REAL_ORDERS='FORBIDDEN',FTMO_REAL='FORBIDDEN',MT5_REAL='FORBIDDEN',generated_at=datetime.now(UTC).isoformat())
        for name,value in [('p79_positions.json',data),('p79_report.json',report)]:
            tmp=OUT/(name+'.tmp')
            tmp.write_text(json.dumps(value,indent=2,ensure_ascii=False,default=str),encoding='utf-8')
            tmp.replace(OUT/name)
        print(json.dumps(report,default=str))
    except Exception:
        for name in ('p79_positions.json','p79_report.json'):
            (OUT/name).unlink(missing_ok=True)
        raise
    finally:
        mt5.shutdown()

if __name__=='__main__':
    run()
