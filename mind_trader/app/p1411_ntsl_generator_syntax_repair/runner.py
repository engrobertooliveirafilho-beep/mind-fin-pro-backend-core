from pathlib import Path
import json
from datetime import datetime, timezone

STATUS = "P14.11_NTSL_GENERATOR_SYNTAX_REPAIR_IMPLEMENTED"

ROOT = Path(".")
EXPORT_DIR = ROOT / "profit_import_package"
REPORT_DIR = ROOT / "reports" / "P14.11_NTSL_GENERATOR_SYNTAX_REPAIR"

NTSL_FILE = EXPORT_DIR / "p1411_minimal_logic_compilable.nts"

NTSL_CODE = """begin
  if Close > Open then
    BuyAtMarket;

  if Close < Open then
    SellShortAtMarket;
end;
"""

def write_ntsl():
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    NTSL_FILE.write_text(NTSL_CODE, encoding="utf-8")
    return NTSL_FILE

def run():
    generated = write_ntsl()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {
        "STATUS": STATUS,
        "GENERATED_FILE": str(generated),
        "NTSL_COMPAT_TARGET": "Profit 5.0.3.254",
        "REAL_ORDERS": "FORBIDDEN",
        "REAL_BROKER": "DISABLED",
        "LIVE": "FORBIDDEN",
        "EDGE": "NOT_PROVEN",
        "CAUSALITY": "NOT_PROVEN",
        "VALIDATION_REQUIRED": "Import generated .nts into Profit and compile manually",
        "CSV_EXPECTED_SUCCESS": {
            "strategy_id": "p1411_minimal_logic_compilable",
            "file": "p1411_minimal_logic_compilable.nts",
            "compiled": "true",
            "error": ""
        },
        "DIFF_LOGIC": [
            "Removed input block to avoid Profit parser incompatibility.",
            "Removed var declarations to validate strategy-command syntax first.",
            "Removed MediaExp and indexed series access for baseline compatibility.",
            "Kept real strategy commands BuyAtMarket and SellShortAtMarket.",
            "Generated minimal logical strategy, not empty begin/end."
        ],
        "EXPORT_READY": True,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    (REPORT_DIR / "P14.11_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (REPORT_DIR / "p1411_example.nts").write_text(NTSL_CODE, encoding="utf-8")

    (REPORT_DIR / "import_instructions.txt").write_text(
        "Importar no Profit: profit_import_package/p1411_minimal_logic_compilable.nts\n"
        "Compilar manualmente.\n"
        "Se compilar, gerar CSV com compiled=true.\n"
        "Se falhar, gerar CSV com compiled=false e erro real.\n",
        encoding="utf-8"
    )

    return manifest

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
