from app.mcul.linguistics.slang_detector import SlangDetector
from app.mcul.normalization.normalizer import SemanticNormalizer
from app.mcul.output.constraint import OutputConstraint

class MCUL:
    def process(self, user_input):
        slang = SlangDetector().detect(user_input)
        norm = SemanticNormalizer().normalize(user_input)
        out = OutputConstraint().enforce(norm)

        return {
            "slang_analysis": slang,
            "semantic": norm,
            "output_policy": out
        }
