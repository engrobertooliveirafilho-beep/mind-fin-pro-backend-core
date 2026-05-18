class QualityMetrics:
    def evaluate(self, user_message: str, response: str, intent: str):
        r = response or ''
        fallback = 'informaÃ§Ã£o registrada' in r.lower() and intent == 'EDUCATIONAL_EXPLANATION'
        return {'intent': intent, 'response_chars': len(r), 'fallback_detected': fallback, 'fallback_rate_target': '<5%', 'tutoring_quality': 'PASS' if len(r) > 100 and not fallback else 'REVIEW'}