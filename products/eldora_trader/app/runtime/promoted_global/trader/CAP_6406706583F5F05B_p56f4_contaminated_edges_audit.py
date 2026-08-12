import os
import psycopg2

trash = {
"adding established genetics along with cu",
"calves because of his",
"clicking your rodeo region below",
"Competition Stats",
"Competition Stats http",
"Daniels",
"Darci Miller",
"GLC",
"his 66 total outs",
"owner Julio Moreno in Merced",
"Page 463",
"Page 77",
"professional Getty Images",
"Sammy Andrews Breeding https",
"the",
"the cow Lady Luck",
"the Professional Bull Riders",
"Unknown. More Bulls",
"World Champion Bucking Bull"
}

conn = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")
cur = conn.cursor()

cur.execute("""
SELECT
    p.id,
    a.official_name AS parent,
    p.relation,
    b.official_name AS child,
    p.confidence_score,
    p.validation_status
FROM p55a_pedigree_edges p
JOIN p55a_animals a ON a.id=p.parent_id
JOIN p55a_animals b ON b.id=p.child_id
ORDER BY a.official_name,b.official_name
""")

rows = cur.fetchall()

print("CONTAMINATED_OR_INVALID_EDGES")
for edge_id,parent,relation,child,confidence,status in rows:
    reasons = []
    if parent in trash:
        reasons.append("TRASH_PARENT")
    if parent == child:
        reasons.append("SELF_PARENT")
    if status == "weak":
        reasons.append("WEAK")
    if confidence <= 35:
        reasons.append("LOW_CONFIDENCE")
    if reasons:
        print(edge_id, "|", parent, "|", relation, "|", child, "|", confidence, "|", status, "|", ",".join(reasons))

conn.close()
