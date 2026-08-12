import json
from pathlib import Path
from app.api.whatsapp import eldora_primary_runtime_reply

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P19O_RUNTIME_EXECUTION_BIAS_ANALYSIS_20260617_175835")

cases = [
    "tenho um mercedes classe A ano 2000, esta com problema no atuador aks o que faço?",
    "ela é semi automatica, desligado entra todas as marchas, mas ligado fica mto dura",
    "não tem erro",
    "é o atuador aks como resolvo?",
]

bad_patterns = [
    "verifique", "siga estes passos", "leve o carro", "diagnóstico do problema",
    "anote os sintomas", "código de erro", "mecânico especializado"
]

expected_patterns = [
    "desacoplando", "embreagem", "curso", "atuador", "haste", "potenciômetro", "garfo"
]

results = []

for msg in cases:
    reply = eldora_primary_runtime_reply("p19o_internal_aks_user", msg)
    low = str(reply or "").lower()

    bad_hits = [p for p in bad_patterns if p in low]
    expected_hits = [p for p in expected_patterns if p in low]

    results.append({
        "input": msg,
        "reply": reply,
        "bad_hits": bad_hits,
        "expected_hits": expected_hits,
        "generic_bias_detected": len(bad_hits) > 0 and len(expected_hits) < 2,
        "status": "PASS" if len(expected_hits) >= 2 and len(bad_hits) == 0 else "FAIL"
    })

fail_count = sum(1 for r in results if r["status"] == "FAIL")
generic_bias = sum(1 for r in results if r["generic_bias_detected"])

report = {
    "mission": "P19O_RUNTIME_EXECUTION_BIAS_ANALYSIS",
    "status": "FAIL" if fail_count > 0 else "PASS",
    "cases": len(results),
    "fail_count": fail_count,
    "generic_bias_count": generic_bias,
    "root_cause": "runtime_real_path_still_prefers_generic_troubleshooting" if generic_bias else "not_detected",
    "production_enabled": False,
    "real_user_sent": False,
    "runtime_modified": False,
    "next_required_action": "P19P_RUNTIME_EXECUTION_BIAS_FIX",
    "results": results
}

(out / "P19O_RUNTIME_EXECUTION_BIAS_ANALYSIS_REPORT.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False))
