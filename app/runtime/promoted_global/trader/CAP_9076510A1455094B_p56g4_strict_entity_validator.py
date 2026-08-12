import re

BLOCK_PREFIXES = [
    "the ",
    "his ",
    "adding ",
    "owner ",
    "professional ",
    "clicking ",
    "calves ",
]

BLOCK_CONTAINS = [
    "http",
    "page ",
    "competition stats",
    "getty images",
    "professional bull riders",
    "world champion bucking bull",
    "total outs",
    "rodeo region",
    "breeding https",
]

BLOCK_EXACT = {
    "the",
    "GLC",
    "Daniels",
    "Darci Miller",
    "Unknown. More Bulls",
    "Unknown Dam",
    "World Champion Bucking Bull",
    "Competition Stats",
}

def normalize_name(name):
    return re.sub(r"\s+", " ", str(name or "").strip())

def validate_animal_entity(name, confidence=None, source_id=None):
    name = normalize_name(name)
    low = name.lower()
    reasons = []

    if not name:
        reasons.append("EMPTY_NAME")

    if len(name) < 4:
        reasons.append("NAME_TOO_SHORT")

    if name in BLOCK_EXACT:
        reasons.append("BLOCK_EXACT")

    if any(low.startswith(p) for p in BLOCK_PREFIXES):
        reasons.append("BLOCK_PREFIX")

    if any(x in low for x in BLOCK_CONTAINS):
        reasons.append("BLOCK_CONTAINS")

    if re.match(r"^page\s+\d+$", low):
        reasons.append("PAGE_FRAGMENT")

    if confidence is not None and float(confidence) <= 40:
        reasons.append("LOW_CONFIDENCE")

    if not source_id:
        reasons.append("MISSING_SOURCE")

    return {
        "input": name,
        "normalized": name,
        "status": "REJECT" if reasons else "PASS",
        "reasons": reasons
    }

def validate_pedigree_edge(parent_name, child_name, relation, confidence=None, source_id=None):
    parent = validate_animal_entity(parent_name, confidence, source_id)
    child = validate_animal_entity(child_name, confidence, source_id)
    reasons = []

    if parent["status"] != "PASS":
        reasons.append("INVALID_PARENT")

    if child["status"] != "PASS":
        reasons.append("INVALID_CHILD")

    if normalize_name(parent_name).lower() == normalize_name(child_name).lower():
        reasons.append("SELF_PARENT")

    if relation not in {"sire", "dam"}:
        reasons.append("INVALID_RELATION")

    if confidence is not None and float(confidence) <= 40:
        reasons.append("LOW_EDGE_CONFIDENCE")

    if not source_id:
        reasons.append("MISSING_EDGE_SOURCE")

    return {
        "parent": parent,
        "child": child,
        "relation": relation,
        "status": "REJECT" if reasons else "PASS",
        "reasons": reasons
    }
