from pathlib import Path
import json
from datetime import datetime, timezone

STATUS = "P14.13_INLINE_NTSL_GENERATOR_PATCH_IMPLEMENTED"

ROOT = Path(".")
EXPORT_DIR = ROOT / "profit_import_package"
REPORT_DIR = ROOT / "reports" / "P14.13_INLINE_NTSL_GENERATOR_PATCH"

NTSL_FILE = EXPORT_DIR / "p1413_inline_media_strategy.nts"

NTSL_CODE = """begin
  if Media(9, Close) > Media(21, Close) then
    BuyAtMarket;

  if Media(9, Close) < Media(21, Close) then
    SellShortAtMarket;
end;
"""

def run():
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    NTSL_FILE.write_text(NTSL_CODE, encoding="utf-8")

    manifest = {
        "STATUS": STATUS,
        "GENERATED_FILE": str(NTSL_FILE),
        "PATCH_DECISION": "Use inline expressions only; avoid input, var, Float until Profit syntax compatibility is proven.",
        "COMPAT_PROVEN": {
            "begin_end": True,
            "close_open_logic": True,
            "buy_at_market": True,
            "sell_short_at_market": True,
            "media_inline": True,
            "var_block": False,
            "input_block": False,
            "media_exp": "UNTESTED",
            "series_indexing": "UNTESTED"
        },
        "REAL_ORDERS": "FORBIDDEN",
        "REAL_BROKER": "DISABLED",
        "LIVE": "FORBIDDEN",
        "EDGE": "NOT_PROVEN",
        "CAUSALITY": "NOT_PROVEN",
        "EXPORT_READY": True,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    (REPORT_DIR / "P14.13_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (REPORT_DIR / "p1413_inline_media_strategy.nts").write_text(NTSL_CODE, encoding="utf-8")

    return manifest

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
