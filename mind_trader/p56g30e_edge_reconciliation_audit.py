import os, json, psycopg2
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal

OUT = Path("reports/P5.6G30_CONTROLLED_PEDIGREE_MUTATION")
OUT.mkdir(parents=True, exist_ok=True)

BUSHWACKER_ID = "fc55d337-491f-458f-b962-d8cc6372a0fb"
REINDEER_MO_ID = "5a87cfa3-c33e-463c-9b5c-30b997d1b962"
DAM_110_ID = "d64d1a1f-01dd-4587-bf18-bf8e3c968cfc"
SOURCE_ID = "df645e3f-d3c9-4eed-a876-d79d052a6f99"

def js(v):
    if isinstance(v, Decimal):
        return float(v)
    return v

conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur = conn.cursor()

cur.execute("""
select id, official_name, registry_number, confidence_score, validation_status
from public.p55a_animals
where id in (%s,%s,%s)
order by official_name;
""", (BUSHWACKER_ID, REINDEER_MO_ID, DAM_110_ID))
nodes = cur.fetchall()

cur.execute("""
select
    e.id,
    e.parent_id,
    e.child_id,
    e.relation,
    e.generation_distance,
    e.validation_status,
    e.confidence_score,
    e.evidence_source_id,
    p.official_name as parent,
    c.official_name as child
from public.p55a_pedigree_edges e
left join public.p55a_animals p on p.id=e.parent_id
left join public.p55a_animals c on c.id=e.child_id
where e.child_id=%s
order by e.relation, e.confidence_score desc nulls last;
""", (BUSHWACKER_ID,))
edges = cur.fetchall()

cur.execute("""
select id, source_url, confidence_score, validation_status
from public.p55a_sources
where id=%s;
""", (SOURCE_ID,))
source = cur.fetchall()

expected = {
    "sire": REINDEER_MO_ID,
    "dam": DAM_110_ID
}

found = {
    "sire": False,
    "dam": False
}

for e in edges:
    edge_id, parent_id, child_id, relation, generation_distance, validation_status, confidence_score, evidence_source_id, parent, child = e
    if relation in expected and str(parent_id) == expected[relation]:
        found[relation] = True

missing = [k for k,v in found.items() if not v]

report = {
    "STATUS": "P56G30E_EDGE_RECONCILIATION_AUDIT_COMPLETED",
    "mode": "READ_ONLY_NO_MUTATION",
    "bushwacker_id": BUSHWACKER_ID,
    "expected_parent_ids": expected,
    "nodes_found": [
        {
            "id": str(r[0]),
            "official_name": r[1],
            "registry_number": r[2],
            "confidence_score": js(r[3]),
            "validation_status": r[4]
        }
        for r in nodes
    ],
    "source_found": [
        {
            "id": str(r[0]),
            "source_url": r[1],
            "confidence_score": js(r[2]),
            "validation_status": r[3]
        }
        for r in source
    ],
    "current_edges": [
        {
            "id": str(r[0]),
            "parent_id": str(r[1]),
            "child_id": str(r[2]),
            "relation": r[3],
            "generation_distance": r[4],
            "validation_status": r[5],
            "confidence_score": js(r[6]),
            "evidence_source_id": str(r[7]) if r[7] else None,
            "parent": r[8],
            "child": r[9]
        }
        for r in edges
    ],
    "expected_edges_found": found,
    "missing_expected_edges": missing,
    "mutation_required": len(missing) > 0,
    "next": "P56G30F_GENERATE_ROLLBACK_SQL_FOR_MISSING_EDGES" if missing else "MISSION_COMPLETE_NO_MUTATION_REQUIRED",
    "generated_at": datetime.now(timezone.utc).isoformat()
}

(OUT / "p56g30e_edge_reconciliation_audit.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

cur.close()
conn.close()

print(json.dumps(report, indent=2, ensure_ascii=False))
