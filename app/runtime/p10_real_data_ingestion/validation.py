import csv, hashlib, io, math
from datetime import datetime
from pathlib import Path

def inspect_csv(path):
    raw=Path(path).read_bytes()
    lines=raw.decode('utf-8-sig').splitlines()
    if not lines: raise ValueError('empty CSV')
    delimiter=max((',', ';', '\t'),key=lambda d:len(next(csv.reader([lines[0]],delimiter=d))))
    reader=csv.reader(io.StringIO(raw.decode('utf-8-sig')),delimiter=delimiter,strict=True)
    cols=[c.strip().lower().strip('<>') for c in next(reader)]
    required={'time','open','high','low','close'}
    missing=sorted(required-set(cols))
    schema=not missing and len(cols)==len(set(cols))
    count=bad=duplicates=0; ordered=True; previous=None; seen=set(); closes=set()
    for row in reader:
        count+=1
        try:
            if not schema or len(row)!=len(cols): raise ValueError('schema')
            d=dict(zip(cols,row)); stamp=(d.get('date','')+' '+d['time']).strip().replace('.','-',2) if 'date' in d else d['time']
            t=datetime.fromisoformat(stamp)
            if t in seen: duplicates+=1
            if previous is not None and t<=previous: ordered=False
            seen.add(t); previous=t
            o,h,l,c=(float(d[k]) for k in ('open','high','low','close'))
            if not all(math.isfinite(v) and v>0 for v in (o,h,l,c)) or not l<=min(o,c)<=max(o,c)<=h: raise ValueError('OHLC')
            closes.add(c)
        except (ValueError,TypeError,OverflowError): bad+=1
    return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),rows=count,columns=sorted(cols),missing_required_columns=missing,schema_ok=schema,duplicate_rows=duplicates,timestamp_order=ordered,invalid_rows=bad,unique_closes=len(closes),quality_pass=schema and count>=200 and bad==duplicates==0 and ordered and len(closes)>1,certified=False,validation_executed=True)
