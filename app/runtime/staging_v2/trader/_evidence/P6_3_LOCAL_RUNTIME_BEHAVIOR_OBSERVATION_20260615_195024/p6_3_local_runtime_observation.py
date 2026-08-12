import json, re, time, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime

P61 = Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P6_1_RUNTIME_BEHAVIOR_TEST_HARNESS_NO_BUILD_20260615_165157")
OUT = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P6_3_LOCAL_RUNTIME_BEHAVIOR_OBSERVATION_20260615_195024")
OUT.mkdir(parents=True, exist_ok=True)

ENDPOINTS = [
    "http://127.0.0.1:8000/webhook/whatsapp",
    "http://127.0.0.1:8001/webhook/whatsapp",
    "https://mind-fin-pro-backend-core-1.onrender.com/webhook/whatsapp"
]

tests = json.loads((P61 / "P6_1_BEHAVIOR_TEST_CASES.json").read_text(encoding="utf-8"))["behavior_tests"]

def post_form(url, body):
    data = urllib.parse.urlencode({
        "Body": body,
        "From": "whatsapp:+5511999999999"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="ignore")

def clean_xml(text):
    return re.sub(r"<[^>]+>", " ", text).strip()

def score_response(test, raw):
    text = clean_xml(raw)
    low = text.lower()
    score = 0
    detected = []

    scoring = test.get("scoring", {})
    cap = test["capability"]

    if "não entendi" in low or "reformule" in low:
        return 0, ["fallback_detected"], text

    if cap == "HIERARCHICAL_PLANNING":
        checks = {
            "explicit_root_goal": ["objetivo raiz", "objetivo principal", "meta principal", "root goal"],
            "hierarchy_depth_2_or_more": ["fase", "etapa", "subtarefa", "nível", "subobjetivo"],
            "dependency_order": ["ordem", "dependência", "sequência", "prioridade"],
            "no_direct_execution": ["não executar", "sem executar", "planejar", "antes de executar"],
            "serializable_structure": ["matriz", "json", "tabela", "estrutura", "plano"]
        }
    else:
        checks = {
            "explicit_verdict": ["allow", "review", "block", "rewrite", "escalate", "permitir", "revisar", "bloquear"],
            "risk_level": ["risco", "baixo", "médio", "alto", "crítico"],
            "rationale": ["motivo", "justificativa", "porque", "razão"],
            "shadow_mode": ["shadow", "simulação", "sem bloquear", "modo sombra"],
            "audit_trace": ["auditoria", "rastro", "trace", "registro", "ledger"]
        }

    for key, weight in scoring.items():
        terms = checks.get(key, [key.replace("_", " ")])
        if any(t in low for t in terms):
            score += int(weight)
            detected.append(key)

    return min(score, 100), detected, text

results = []
endpoint_health = []

for endpoint in ENDPOINTS:
    try:
        health_url = endpoint.replace("/webhook/whatsapp", "/health")
        with urllib.request.urlopen(health_url, timeout=5) as r:
            endpoint_health.append({"endpoint": endpoint, "health": r.status, "ok": True})
    except Exception as e:
        endpoint_health.append({"endpoint": endpoint, "health": None, "ok": False, "error": str(e)})

for test in tests:
    selected = None

    for endpoint in ENDPOINTS:
        try:
            raw = post_form(endpoint, test["prompt"])
            score, detected, cleaned = score_response(test, raw)
            selected = {
                "test_id": test["test_id"],
                "capability": test["capability"],
                "endpoint": endpoint,
                "prompt": test["prompt"],
                "raw_response": raw,
                "clean_response": cleaned,
                "score": score,
                "signals_detected": detected,
                "ok": True
            }
            break
        except Exception as e:
            selected = {
                "test_id": test["test_id"],
                "capability": test["capability"],
                "endpoint": endpoint,
                "prompt": test["prompt"],
                "score": 0,
                "signals_detected": [],
                "ok": False,
                "error": str(e)
            }

    results.append(selected)
    time.sleep(1)

by_cap = {}
for cap in sorted(set(r["capability"] for r in results)):
    arr = [r for r in results if r["capability"] == cap]
    avg = sum(r["score"] for r in arr) / max(1, len(arr))
    by_cap[cap] = {
        "avg_score": round(avg, 2),
        "coverage": "LOW" if avg < 70 else "PARTIAL" if avg < 85 else "HIGH",
        "real_gain_if_integrated": "HIGH" if avg < 70 else "MEDIUM" if avg < 85 else "LOW",
        "tests": arr
    }

final = {
    "mission": "P6.3_LOCAL_RUNTIME_BEHAVIOR_OBSERVATION",
    "created_at": datetime.now().isoformat(),
    "endpoint_health": endpoint_health,
    "results": results,
    "capability_delta": by_cap,
    "build_allowed": False,
    "integration_allowed": False,
    "code_changed": False
}

(OUT / "P6_3_ENDPOINT_HEALTH.json").write_text(json.dumps(endpoint_health, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "P6_3_LOCAL_RUNTIME_BEHAVIOR_RESULTS.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "P6_3_CAPABILITY_DELTA_VERDICT.json").write_text(json.dumps(by_cap, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "P6_3_FINAL_STATUS.json").write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps({
    "STATUS": "P6_3_COMPLETE",
    "endpoint_health": endpoint_health,
    "capability_delta": by_cap,
    "build_allowed": False,
    "output": str(OUT)
}, ensure_ascii=False, indent=2))
