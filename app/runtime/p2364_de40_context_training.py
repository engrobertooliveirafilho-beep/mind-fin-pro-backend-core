from pathlib import Path
import pandas as pd
import numpy as np

def classify_context(df):

    df["return"] = df["close"].pct_change()

    vol = df["return"].rolling(20).std()

    trend = (
        df["close"].rolling(50).mean() -
        df["close"].rolling(200).mean()
    )

    conditions = []

    for t,v in zip(trend.fillna(0),vol.fillna(0)):

        if abs(t) < 0.001:
            regime="RANGE"
        elif t > 0:
            regime="UPTREND"
        else:
            regime="DOWNTREND"

        if v > vol.quantile(.70):
            volreg="HIGH_VOL"
        elif v < vol.quantile(.30):
            volreg="LOW_VOL"
        else:
            volreg="NORMAL_VOL"

        conditions.append(f"{regime}|{volreg}")

    df["context"]=conditions

    return df

def train_context_edges(csv_file):

    df=pd.read_csv(csv_file,sep=";")

    for c in df.columns:
        df[c]=pd.to_numeric(df[c],errors="ignore")

    df=classify_context(df)

    df["future"]=df["close"].shift(-10)-df["close"]

    result=[]

    for ctx,g in df.groupby("context"):

        wins=(g["future"]>0).sum()
        losses=(g["future"]<=0).sum()

        total=max(1,wins+losses)

        result.append({
            "context":ctx,
            "samples":total,
            "win_rate":round(wins*100/total,2),
            "avg_move":round(g["future"].mean(),4)
        })

    return pd.DataFrame(result)

if __name__=="__main__":
    pass
