import json
from app.intent.intent_classifier_v2 import IntentClassifierV2
from app.runtime.response_generation_engine import ResponseGenerationEngine
from app.observability.quality_metrics import QualityMetrics

tests = [
    ('me explique derivadas', 'EDUCATIONAL_EXPLANATION'),
    ('qual meu nome?', 'MEMORY_QUERY'),
    ('oi', 'CONVERSATION'),
    ('resuma este conteÃºdo', 'SUMMARIZATION'),
]
c = IntentClassifierV2()
e = ResponseGenerationEngine()
q = QualityMetrics()
results = []
ok_all = True
for msg, exp in tests:
    r = c.classify(msg)
    ans = e.generate(msg, r.intent)
    met = q.evaluate(msg, ans, r.intent)
    ok = r.intent == exp and not met.get('fallback_detected', False)
    ok_all = ok_all and ok
    results.append({'message': msg, 'expected': exp, 'actual': r.intent, 'pass': ok, 'response': ans, 'quality': met})
print(json.dumps({'all_pass': ok_all, 'status_final': 'NEURA_COGNITIVE_STUDENT_PLATFORM_OPERATIONAL' if ok_all else 'FAILED', 'results': results}, ensure_ascii=False, indent=2))
exit(0 if ok_all else 1)