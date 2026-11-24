import pandas as pd
import numpy as np
import argparse, json, hashlib
from pathlib import Path

def rank_contexts(df):
    df = df.copy().reset_index(drop=True)
    df['time'] = pd.to_datetime(df.time, errors='raise')
    cols = ['open','high','low','close','spread']
    df[cols] = df[cols].apply(pd.to_numeric, errors='raise')
    if len(df)<1000 or not df.time.is_monotonic_increasing or df.time.duplicated().any() or not np.isfinite(df[cols]).all().all() or (df[cols[:4]]<=0).any().any() or (df.spread<0).any() or (df.high<df[['open','close','low']].max(axis=1)).any() or (df.low>df[['open','close']].min(axis=1)).any() or not (df.symbol.eq('DE40') & df.timeframe.eq('M5')).all():
        raise ValueError('invalid dataset')
    cut = len(df)*7//10
    horizon=12
    close=df.close
    ma50=close.rolling(50).mean(); ma200=close.rolling(200).mean()
    vol=close.pct_change().rolling(20).std()
    q30,q70=vol.iloc[:cut].quantile([.3,.7])
    threshold=close.iloc[:cut].median()*.0005
    regime=np.select([abs(ma50-ma200)<threshold,ma50>ma200],['RANGE','UPTREND'],default='DOWNTREND')
    volatility=np.select([vol>=q70,vol<=q30],['HIGH_VOL','LOW_VOL'],default='NORMAL_VOL')
    structure=np.select([close>df.high.rolling(20).max().shift(1),close<df.low.rolling(20).min().shift(1)],['BREAKOUT_UP','BREAKOUT_DOWN'],default='NEUTRAL')
    df['context']=pd.Series(regime)+'|'+pd.Series(volatility)+'|SERVER_HOUR_'+df.time.dt.hour.astype(str)+'|'+pd.Series(structure)
    # Enter next bar open; exit after 12 bars. Exclude gaps and last unverified candle.
    df['move']=close.shift(-horizon)-df.open.shift(-1)
    valid=ma200.notna() & vol.notna() & ((df.time.shift(-horizon)-df.time)==pd.Timedelta(minutes=60))
    train=df.loc[valid & (df.index<cut-horizon)]
    test=df.loc[valid & (df.index>=cut) & (df.index<len(df)-horizon-1)]
    rows=[]
    for ctx,g in train.groupby('context'):
        if len(g)<100: continue
        side=1 if g.move.mean()>=0 else -1
        t=test.loc[test.context==ctx,'move']*side
        rows.append(dict(context=ctx,side='BUY' if side==1 else 'SELL',train_samples=len(g),train_gross_expectancy=float((g.move*side).mean()),test_samples=len(t),test_gross_expectancy=float(t.mean()) if len(t) else None,decision='RESEARCH_ONLY'))
    return rows,dict(train_end=str(df.time.iloc[cut-1]),test_start=str(df.time.iloc[cut]),train_samples=len(train),test_samples=len(test),contexts=len(rows),promoted=0,mode='PAPER_ONLY',costs_verified=False,timezone_verified=False,overlapping_labels=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('dataset',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    rows,summary=rank_contexts(pd.read_csv(a.dataset,sep=';'));summary['sha256']=hashlib.sha256(a.dataset.read_bytes()).hexdigest();a.output.write_text(json.dumps(dict(summary=summary,rows=rows),allow_nan=False,indent=2));print(json.dumps(summary))
if __name__=='__main__': main()
