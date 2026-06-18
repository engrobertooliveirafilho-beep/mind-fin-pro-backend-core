import os, json, re, urllib.request

PRICE_RE=re.compile(r"(?i)(?:\$|usd\s*)\s?([0-9]{2,3}(?:[,\.][0-9]{3})*(?:\.[0-9]{2})?|[0-9]{4,8})")
TERMS={
    "semen_price":["semen","straw"],
    "embryo_price":["embryo"],
    "pregnancy_price":["pregnancy","bred cow","recipient"],
    "breeding_fee":["breeding fee","stud fee"],
    "auction_sale":["auction","sold","sale","buyer","consigned"]
}

def parse_price(text):
    vals=[]
    for m in PRICE_RE.findall(str(text or "")):
        n=m.replace(",","")
        try: vals.append(float(n))
        except Exception: pass
    return vals

def classify_market_event(text):
    t=str(text or "").lower()
    for k,terms in TERMS.items():
        if any(x in t for x in terms):
            return k
    return "market_price"

class MarketValuationRealPrices:
    def __init__(self,url=None,key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self,method,path,payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(self.url+path,data=data,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"return=representation"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def animals(self):
        return self.req("GET","/rest/v1/p55a_animals?select=id,official_name&limit=10000")

    def sources(self):
        return self.req("GET","/rest/v1/p55a_sources?select=id,source_url,title,raw_payload&limit=10000")

    def clear_old(self):
        old=self.req("GET","/rest/v1/p55a_valuation_events?event_type=eq.P5.6D_MARKET_PRICE&select=id&limit=10000")
        for r in old:
            self.req("DELETE",f"/rest/v1/p55a_valuation_events?id=eq.{r['id']}")

    def run_once(self):
        self.clear_old()
        animals=self.animals()
        sources=self.sources()
        written=[]
        for a in animals:
            name=(a.get("official_name") or "").lower()
            if not name: continue
            for s in sources:
                blob=" ".join([str(s.get("title") or ""),str(s.get("source_url") or ""),json.dumps(s.get("raw_payload") or {},ensure_ascii=False)])
                if name not in blob.lower(): continue
                prices=parse_price(blob)
                if not prices: continue
                event=classify_market_event(blob)
                price=max(prices)
                payload={
                    "animal_id":a["id"],
                    "event_type":"P5.6D_MARKET_PRICE",
                    "amount":price,
                    "currency":"USD",
                    "source_id":s["id"],
                    "raw_payload":{
                        "mission":"P5.6D",
                        "official_name":a.get("official_name"),
                        "classified_market_event":event,
                        "prices_detected":prices[:20],
                        "source_title":s.get("title"),
                        "source_url":s.get("source_url")
                    },
                    "confidence_score":45,
                    "validation_status":"needs_review"
                }
                if event=="semen_price": payload["semen_price"]=price
                if event=="embryo_price": payload["embryo_price"]=price
                if event=="pregnancy_price": payload["pregnancy_price"]=price
                if event=="breeding_fee": payload["breeding_fee"]=price
                written.append(self.req("POST","/rest/v1/p55a_valuation_events",payload)[0])
        return {"status":"P5.6D_MARKET_VALUATION_REAL_PRICES_DONE","market_events_created":len(written),"top":sorted(written,key=lambda x:x["amount"],reverse=True)[:10],"next_action":"P5.6E_REPRODUCTION_RECORD_ACQUISITION"}
