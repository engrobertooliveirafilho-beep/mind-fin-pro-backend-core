from pathlib import Path
import json
from datetime import datetime, timezone

STATUS = "P14.16A_RISK_SYNTAX_LADDER_IMPLEMENTED"

ROOT = Path(".")
EXPORT_DIR = ROOT / "profit_import_package"
REPORT_DIR = ROOT / "reports" / "P14.16A_RISK_SYNTAX_LADDER"

TEMPLATES = {
    "p1416a_l1_trend_filter": """begin
  if (Media(9, Close) > Media(21, Close)) and (Close > Media(200, Close)) then
    BuyAtMarket;

  if (Media(9, Close) < Media(21, Close)) and (Close < Media(200, Close)) then
    SellShortAtMarket;
end;
""",

    "p1416a_l2_stop_points_probe": """begin
  if (Media(9, Close) > Media(21, Close)) and (Close > Media(200, Close)) then
    BuyAtMarket;

  if (Media(9, Close) < Media(21, Close)) and (Close < Media(200, Close)) then
    SellShortAtMarket;

  SellToCoverStop(Close - 100);
  BuyToCoverStop(Close + 100);
end;
""",

    "p1416a_l3_take_points_probe": """begin
  if (Media(9, Close) > Media(21, Close)) and (Close > Media(200, Close)) then
    BuyAtMarket;

  if (Media(9, Close) < Media(21, Close)) and (Close < Media(200, Close)) then
    SellShortAtMarket;

  SellToCoverLimit(Close + 200);
  BuyToCoverLimit(Close - 200);
end;
""",

    "p1416a_l4_stop_take_probe": """begin
  if (Media(9, Close) > Media(21, Close)) and (Close > Media(200, Close)) then
    BuyAtMarket;

  if (Media(9, Close) < Media(21, Close)) and (Close < Media(200, Close)) then
    SellShortAtMarket;

  SellToCoverStop(Close - 100);
  SellToCoverLimit(Close + 200);

  BuyToCoverStop(Close + 100);
  BuyToCoverLimit(Close - 200);
end;
"""
}

def run():
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    generated = []
    for name, code in TEMPLATES.items():
        path = EXPORT_DIR / f"{name}.nts"
        path.write_text(code, encoding="utf-8")
        generated.append(str(path))

    manifest = {
        "STATUS": STATUS,
        "GENERATED_FILES": generated,
        "VALIDATION_ORDER": list(TEMPLATES.keys()),
        "KNOWN_COMPILED_BASE": [
            "begin/end",
            "BuyAtMarket",
            "SellShortAtMarket",
            "Media() inline"
        ],
        "UNPROVEN_RISK_COMMANDS": [
            "SellToCoverStop",
            "BuyToCoverStop",
            "SellToCoverLimit",
            "BuyToCoverLimit"
        ],
        "STOP_RULE": "Compile one level at a time in Profit. Stop on first syntax error.",
        "REAL_ORDERS": "FORBIDDEN",
        "REAL_BROKER": "DISABLED",
        "LIVE": "FORBIDDEN",
        "EDGE": "NOT_PROVEN",
        "CAUSALITY": "NOT_PROVEN",
        "EXPORT_READY": True,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    (REPORT_DIR / "P14.16A_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return manifest

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
