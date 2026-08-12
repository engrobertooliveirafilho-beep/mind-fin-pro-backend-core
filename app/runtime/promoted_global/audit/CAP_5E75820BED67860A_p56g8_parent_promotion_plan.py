import json
from datetime import datetime, timezone

ids = {
  "Lady Luck": "f49e72fa-e242-4bc0-afbe-5399171c21e7",
  "Whitewater Skoal": "b15c7bb4-ba7f-4f05-9525-bb968e4b8906"
}

sql = """
BEGIN;

UPDATE p55a_animals
SET validation_status='provisional',
    confidence_score=60,
    notes = COALESCE(notes,'') || ' | P5.6G8 promoted parent after media/biomechanics/judge/reproduction/pedigree audit'
WHERE id IN (
  'f49e72fa-e242-4bc0-afbe-5399171c21e7',
  'b15c7bb4-ba7f-4f05-9525-bb968e4b8906'
);

COMMIT;
"""

rollback = """
BEGIN;

UPDATE p55a_animals
SET validation_status='weak',
    confidence_score=40
WHERE id IN (
  'f49e72fa-e242-4bc0-afbe-5399171c21e7',
  'b15c7bb4-ba7f-4f05-9525-bb968e4b8906'
);

COMMIT;
"""

open("P56G8_PARENT_PROMOTION_PLAN.sql","w",encoding="utf-8").write(sql)
open("P56G8_PARENT_PROMOTION_ROLLBACK.sql","w",encoding="utf-8").write(rollback)

snapshot = {
  "mission": "P5.6G8_PARENT_PROMOTION_PLAN",
  "created_at": datetime.now(timezone.utc).isoformat(),
  "mode": "PLAN_ONLY_NO_MUTATION",
  "promotion_candidates": ids,
  "target_status": "provisional",
  "target_confidence_score": 60
}

open("P56G8_PARENT_PROMOTION_PLAN.json","w",encoding="utf-8").write(json.dumps(snapshot,indent=2,ensure_ascii=False))
print(json.dumps(snapshot,indent=2,ensure_ascii=False))
