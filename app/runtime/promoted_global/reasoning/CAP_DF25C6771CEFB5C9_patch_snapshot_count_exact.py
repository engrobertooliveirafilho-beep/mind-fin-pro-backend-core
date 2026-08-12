from pathlib import Path

p=Path("app/mind/p5_5z_executive_snapshot/snapshot.py")
s=p.read_text(encoding="utf-8")

old='''    def count(self, table):
        return len(self.req("GET",f"/rest/v1/{table}?select=id&limit=10000"))
'''

new='''    def count(self, table):
        import urllib.request
        r=urllib.request.Request(
            self.url+f"/rest/v1/{table}?select=id&limit=1",
            headers={
                "apikey":self.key,
                "Authorization":f"Bearer {self.key}",
                "Prefer":"count=exact"
            },
            method="GET"
        )
        with urllib.request.urlopen(r,timeout=30) as x:
            cr=x.headers.get("Content-Range") or x.headers.get("content-range") or "0-0/0"
        return int(str(cr).split("/")[-1])
'''

if old not in s:
    raise SystemExit("COUNT_BLOCK_NOT_FOUND")

p.write_text(s.replace(old,new),encoding="utf-8")
print("SNAPSHOT_COUNT_PATCHED")
