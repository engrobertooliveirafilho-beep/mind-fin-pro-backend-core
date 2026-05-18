from pathlib import Path

p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

if "NEURA_ROUTE_AUDIT_ENDPOINT" not in s:
    s += r'''

# NEURA_ROUTE_AUDIT_ENDPOINT
@app.get("/routes")
async def neura_route_audit():
    return sorted([getattr(r, "path", "") for r in app.routes])
'''
p.write_text(s, encoding="utf-8")
