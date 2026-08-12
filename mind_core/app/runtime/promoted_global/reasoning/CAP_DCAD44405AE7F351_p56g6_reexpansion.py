import json
from datetime import datetime, timezone
from app.mind.p5_5v_pedigree_extractor.extractor import PedigreeExtractor

e = PedigreeExtractor()

result = e.run_once(limit=250)

snapshot = {
    "mission": "P5.6G6_SOURCE_BACKED_PEDIGREE_REEXPANSION",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "mode": "LIVE_RUN_WITH_STRICT_VALIDATOR",
    "result": result
}

open("P56G6_SOURCE_BACKED_PEDIGREE_REEXPANSION.json","w",encoding="utf-8").write(
    json.dumps(snapshot,indent=2,ensure_ascii=False,default=str)
)

print(json.dumps(snapshot,indent=2,ensure_ascii=False,default=str))
