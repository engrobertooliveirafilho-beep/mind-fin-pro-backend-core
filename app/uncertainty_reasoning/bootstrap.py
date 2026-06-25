from app.uncertainty_reasoning.hypothesis_engine.engine import HypothesisEngine
from app.uncertainty_reasoning.scoring_engine.scorer import ProbabilityScorer
from app.uncertainty_reasoning.resolver.resolver import IntentResolver

class URE:
    def process(self, input_text, context):
        h = HypothesisEngine().generate(input_text)
        s = ProbabilityScorer().score(h, context)
        return IntentResolver().resolve(s)
