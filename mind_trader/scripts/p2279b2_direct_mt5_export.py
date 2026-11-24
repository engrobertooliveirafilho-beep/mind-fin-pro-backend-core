from pathlib import Path
from datetime import datetime, timezone
import csv, hashlib, argparse

symbols_target = [
    "EURUSD","GBPUSD","USDJPY","USDCHF","AUDUSD","NZDUSD","USDCAD",
    "XAUUSD","US100","US500","GER40","UK100","JP225"
]

aliases = {
    "US100": ["US100","USTEC","NAS100","NAS100.cash","US100.cash"],
    "US500": ["US500","SPX500","SP500","US500.cash"],
    "GER40": ["GER40","GER30","DE40","DAX40","GER40.cash"],
    "UK100": ["UK100","FTSE100","UK100.cash"],
    "JP225": ["JP225","JPN225","NIKKEI","JP225.cash"],
}

def resolve_symbol(target, available):
    if target in available:
        return target
    matches = set(aliases.get(target, [])) & set(available)
    return next(iter(matches)) if len(matches) == 1 else None


def export(mt5, out, ev):
    out, ev = Path(out), Path(ev)
    out.mkdir(parents=True, exist_ok=True)
    ev.mkdir(parents=True, exist_ok=True)
    timeframes = {name: (getattr(mt5, 'TIMEFRAME_'+name), count) for name,count in [('M15',5000),('M30',5000),('H1',5000),('H4',3000),('D1',1500)]}
    if not mt5.initialize():
        raise RuntimeError('MT5 initialization failed')
    manifest = []
    try:
        available = [s.name for s in mt5.symbols_get() or []]
        with (ev / 'p2279b2_export_manifest.csv').open('x', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['target_symbol','broker_symbol','timeframe','status','rows','file','error','sha256'])
            for target in symbols_target:
                broker = resolve_symbol(target, available)
                selected = bool(broker and mt5.symbol_select(broker, True))
                for name,(tf,bars) in timeframes.items():
                    file = out / f'MT5_{target}_{name}_raw.csv'
                    row = [target,broker or '',name,'SYMBOL_UNAVAILABLE',0,'','','']
                    if selected:
                        rates = mt5.copy_rates_from_pos(broker,tf,1,bars)
                        if rates is None or len(rates)==0:
                            row[3]='NO_DATA'
                        else:
                            try:
                                with file.open('x',newline='',encoding='utf-8') as dest:
                                    writer=csv.writer(dest)
                                    writer.writerow(['time','open','high','low','close','tick_volume','spread','real_volume'])
                                    for r in rates:
                                        writer.writerow([datetime.fromtimestamp(int(r['time']),timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),*[r[k] for k in ('open','high','low','close')],*[int(r[k]) for k in ('tick_volume','spread','real_volume')]])
                                row[3:]=['RAW_SAVED',len(rates),str(file),'',hashlib.sha256(file.read_bytes()).hexdigest()]
                            except FileExistsError:
                                row[3]='EXISTS_BLOCKED'
                    w.writerow(row)
                    f.flush()
                    manifest.append(row)
    finally:
        mt5.shutdown()
    return manifest

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    parser.add_argument('--evidence',required=True)
    args=parser.parse_args()
    import MetaTrader5 as mt5
    rows=export(mt5,args.out,args.evidence)
    print({'mode':'PAPER_ONLY','real_orders':'FORBIDDEN','total_slots':len(rows),'ready_slots':sum(r[3]=='RAW_SAVED' and r[4]>=500 for r in rows)})
