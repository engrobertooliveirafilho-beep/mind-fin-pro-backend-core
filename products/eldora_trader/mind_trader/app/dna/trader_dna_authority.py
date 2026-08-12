import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

REQUIRED_ATOM_FIELDS=["context","trigger","invalidation","target","risk","success_conditions"]

def dna_atom_id(atom):
    raw=json.dumps(atom,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

def create_dna_atom(name, category, **fields):
    missing=[k for k in REQUIRED_ATOM_FIELDS if k not in fields or fields[k] in [None,""]]
    atom={
        "name":name,
        "category":category,
        **fields,
        "created_at":datetime.now(UTC).isoformat(),
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }
    atom["missing"]=missing
    atom["valid"]=not missing
    atom["atom_id"]=dna_atom_id({k:v for k,v in atom.items() if k not in ["created_at","atom_id"]})
    return atom

def validate_dna_atom(atom):
    missing=[k for k in REQUIRED_ATOM_FIELDS if k not in atom or atom[k] in [None,""]]
    return {
        "valid":not missing,
        "missing":missing,
        "decision":"DNA_ATOM_OK" if not missing else "DNA_ATOM_BLOCKED",
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }

def save_dna_atoms(atoms,path="mind_trader/reports/P8.86_trader_dna_atoms.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(atoms,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
