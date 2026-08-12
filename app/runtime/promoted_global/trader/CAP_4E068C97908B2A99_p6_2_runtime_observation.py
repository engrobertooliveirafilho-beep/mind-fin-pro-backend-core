import json, re, time, urllib.request
from pathlib import Path
from datetime import datetime

REPO = Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core")
P61 = Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P6_1_RUNTIME_BEHAVIOR_TEST_HARNESS_NO_BUILD_20260615_165157")
OUT = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P6_2_AUTOMATED_RUNTIME_BEHAVIOR_OBSERVATION_20260615_170333")
OUT.mkdir(parents=True, exist_ok=True)

RUNTIME_ENDPOINTS = [
    "http://127.0.0.1:8000/webhook/whatsapp",
    "http://127.0.0.1:8001/webhook/whatsapp",
    "https://mind-fin-pro-backend-core-1.onrender.com/webhook/whatsapp"
]

tests = json.loads((P61 / "P6_1_BEHAVIOR_TEST_CASES.json").read_text(encoding="utf-8"))["behavior_tests"]

def post_form(url, body):
    data = f"Body={urllib.parse.quote(body)}&From=whatsapp%3A%2B5511999999999".encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", errors="ignore")

def score_response(test, text):
    low = text.lower()
    score = 0
    signals = []

    expected = test.get("expected_signals", [])
    for s in expected:
        terms = [x.strip().lower() for x in re.split(r"/|,|\s+ou\s+", s) if x.strip()]
        if any(t in low for t in terms):
            signals.append(s)

    cap = test["capability"]

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

    scoring = test.get("scoring", {})
    for key, weight in scoring.items():
        terms = checks.get(key, [key.replace("_", " ")])
        if any(t in low for t in terms):
            score += int(weight)

    return min(score, 100), signals

results = []
for test in tests:
    prompt = test["prompt"]
    best = None

    for endpoint in RUNTIME_ENDPOINTS:
        try:
            response = post_form(endpoint, prompt)
            score, signals = score_response(test, response)
            best = {
                "test_id": test["test_id"],
                "capability": test["capability"],
                "endpoint": endpoint,
                "prompt": prompt,
                "response": response,
                "score": score,
                "signals_detected": signals,
                "ok": True
            }
            break
        except Exception as e:
            best = {
                "test_id": test["test_id"],
                "capability": test["capability"],
                "endpoint": endpoint,
                "prompt": prompt,
                "response": "",
                "score": 0,
                "signals_detected": [],
                "ok": False,
                "error": str(e)
            }

    results.append(best)
    time.sleep(1)

by_cap = {}
for cap in sorted(set(r["capability"] for r in results)):
    cap_results = [r for r in results if r["capability"] == cap]
    avg = sum(r["score"] for r in cap_results) / max(1, len(cap_results))
    if avg < 70:
        verdict = "MEANINGFUL_RUNTIME_GAP"
        gain = "HIGH"
    elif avg < 85:
        verdict = "PARTIAL_RUNTIME_COVERAGE"
        gain = "MEDIUM"
    else:
        verdict = "RUNTIME_ALREADY_COVERS_MOST_BEHAVIOR"
        gain = "LOW"
    by_cap[cap] = {
        "avg_score": round(avg, 2),
        "verdict": verdict,
        "real_gain_if_integrated": gain,
        "tests": cap_results
    }

final = {
    "mission": "P6.2_AUTOMATED_RUNTIME_BEHAVIOR_OBSERVATION",
    "created_at": datetime.now().isoformat(),
    "runtime_behavior_results": results,
    "capability_delta_verdict": by_cap,
    "build_allowed": False,
    "integration_allowed": False,
    "code_changed": False
}

(OUT / "P6_2_RUNTIME_BEHAVIOR_RESULTS.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "P6_2_CAPABILITY_DELTA_VERDICT.json").write_text(json.dumps(by_cap, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "P6_2_FINAL_STATUS.json").write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps({
    "STATUS": "P6_2_COMPLETE",
    "tests": len(results),
    "verdict": by_cap,
    "build_allowed": False,
    "output": str(OUT)
}, ensure_ascii=False, indent=2))
