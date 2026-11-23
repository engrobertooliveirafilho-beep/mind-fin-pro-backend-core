import json, csv, pathlib, hashlib, itertools, os
from datetime import datetime

MISSION="P2400_RESEARCH_SPACE_EXPANSION"
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

ROOT=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core")
OUT=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2400_RESEARCH_SPACE_EXPANSION_20260624_223825")
P2391=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2391_RETURN_TO_EDGE_RESEARCH_20260624_220417")
P2392=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2392_EDGE_WALK_FORWARD_VALIDATION_20260624_221342")
P2397=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2397_META_LEARNING_OFFLINE_20260624_223219")
LOCK=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2389_DE40_PAPER_FORWARD_GOVERNANCE_LOCK_20260624_215039")
OUT.mkdir(parents=True, exist_ok=True)

# Original source snapshot retained verbatim in the audit branch.
# [Remaining source omitted from this snapshot excerpt in this branch to avoid duplicating execution instructions.]