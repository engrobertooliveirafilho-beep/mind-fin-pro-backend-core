import json, csv, re
from pathlib import Path
from datetime import datetime, UTC

RAW=Path("data/incoming/profit_raw_backtests")
OUT=Path("data/incoming/profit_real_backtests")

ALIASES={
 "strategy_id":["strategy_id","estrategia","estratégia","strategy","nome","name"],
 "asset":["asset","ativo","symbol","ticker"],
 "timeframe":["timeframe","periodo","período","tempo","grafico","gráfico"],
 "profit_factor":["profit_factor","fator_lucro","fator de lucro","profit factor","pf"],
 "drawdown":["drawdown","dd","rebaixamento","max_drawdown","drawdown máximo"],
 "winrate":["winrate","taxa_acerto","taxa de acerto","percentual acerto","acerto"],
 "trades":["trades","operações","operacoes","numero_operacoes","número de operações"],
 "payoff":["payoff","pay_off","resultado_medio","resultado médio","media_trade","média trade"]
}

def norm(s):
    return re.sub(r"[^a-z0-9]+","_",str(s).strip().lower()).strip("_")

def map_columns(cols):
    normalized={norm(c):c for c in cols}
    mapping={}
    for target,names in ALIASES.items():
        for n in names:
            key=norm(n)
            if key in normalized:
                mapping[target]=normalized[key]
                break
    return mapping

def normalize_file(path):
    p=Path(path)
    with open(p,newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        rows=list(reader)
        mapping=map_columns(reader.fieldnames or [])
    out_rows=[]
    for i,r in enumerate(rows):
        item={}
        for target in ALIASES:
            src=mapping.get(target)
            item[target]=r.get(src,"") if src else ""
        if not item["strategy_id"]:
            item["strategy_id"]=p.stem+"_"+str(i+1)
        out_rows.append(item)
    return {"source":str(p),"mapping":mapping,"rows":out_rows}

def run():
    RAW.mkdir(parents=True,exist_ok=True)
    OUT.mkdir(parents=True,exist_ok=True)
    normalized=[]
    for f in RAW.glob("*.csv"):
        result=normalize_file(f)
        out_file=OUT/(f.stem+"_normalized.csv")
        with open(out_file,"w",newline="",encoding="utf-8") as fh:
            w=csv.DictWriter(fh,fieldnames=list(ALIASES.keys()))
            w.writeheader()
            w.writerows(result["rows"])
        normalized.append({"source":result["source"],"target":str(out_file),"rows":len(result["rows"]),"mapping":result["mapping"]})
    report_dir=Path("reports/P15.2_PROFIT_BACKTEST_EXPORT_NORMALIZER")
    report_dir.mkdir(parents=True,exist_ok=True)
    manifest={
        "STATUS":"P15.2_PROFIT_BACKTEST_EXPORT_NORMALIZER_IMPLEMENTED",
        "RAW_FILES":len(list(RAW.glob("*.csv"))),
        "NORMALIZED_FILES":len(normalized),
        "OUTPUT_DIR":str(OUT),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"RUN_P15.1_AFTER_PROFIT_EXPORT",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (report_dir/"normalization_report.json").write_text(json.dumps(normalized,indent=2,ensure_ascii=False),encoding="utf-8")
    (report_dir/"P15.2_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
