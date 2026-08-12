from pathlib import Path
import json
from datetime import datetime, timezone

STATUS = "P14.12_NTSL_TEMPLATE_LADDER_IMPLEMENTED"

ROOT = Path(".")
EXPORT_DIR = ROOT / "profit_import_package"
REPORT_DIR = ROOT / "reports" / "P14.12_NTSL_TEMPLATE_LADDER"

TEMPLATES = {
    "p1412_l1_empty": """begin
end;
""",
    "p1412_l2_close_open_logic": """begin
  if Close > Open then
    BuyAtMarket;

  if Close < Open then
    SellShortAtMarket;
end;
""",
    "p1412_l3_directional_if_only": """begin
  if Close > Close[1] then
    BuyAtMarket;

  if Close < Close[1] then
    SellShortAtMarket;
end;
""",
    "p1412_l4_single_media": """var
  ma : Float;

begin
  ma := Media(9, Close);

  if Close > ma then
    BuyAtMarket;

  if Close < ma then
    SellShortAtMarket;
end;
""",
    "p1412_l5_dual_media": """var
  fastMA, slowMA : Float;

begin
  fastMA := Media(8, Close);
  slowMA := Media(34, Close);

  if fastMA > slowMA then
    BuyAtMarket;

  if fastMA < slowMA then
    SellShortAtMarket;
end;
"""
}

def generate():
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    generated = []
    for name, code in TEMPLATES.items():
        path = EXPORT_DIR / f"{name}.nts"
        path.write_text(code, encoding="utf-8")
        generated.append(str(path))

    manifest = {
        "STATUS": STATUS,
        "PURPOSE": "Generate Profit NTSL templates by syntax-complexity ladder",
        "NTSL_COMPAT_TARGET": "Profit 5.0.3.254",
        "GENERATED_FILES": generated,
        "VALIDATION_ORDER": list(TEMPLATES.keys()),
        "STOP_RULE": "If one level fails in Profit, do not validate higher levels until syntax is repaired.",
        "REAL_ORDERS": "FORBIDDEN",
        "REAL_BROKER": "DISABLED",
        "LIVE": "FORBIDDEN",
        "EDGE": "NOT_PROVEN",
        "CAUSALITY": "NOT_PROVEN",
        "EXPORT_READY": True,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    (REPORT_DIR / "P14.12_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    csv_template = "strategy_id,file,compiled,error\n"
    for name in TEMPLATES:
        csv_template += f"{name},{name}.nts,false,PENDING_PROFIT_VALIDATION\n"

    (REPORT_DIR / "compile_result_template.csv").write_text(csv_template, encoding="utf-8")
    return manifest

def run():
    return generate()

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
