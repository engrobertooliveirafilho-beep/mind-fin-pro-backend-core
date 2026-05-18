from app.human.multi_llm_runtime import MultiLLMRuntime
from app.vision.consensus_judge import ConsensusJudge

class MultiVisionConsensusRuntime:

    def __init__(self):
        self.llm = MultiLLMRuntime()
        self.judge = ConsensusJudge()

    def refine(self, question, base_analysis):

        prompts = [
            f"Faça uma análise técnica aprofundada:\n{base_analysis}",
            f"Critique possíveis erros e incertezas:\n{base_analysis}",
            f"Extraia hipóteses úteis sobre modelo, ano, ambiente e objetos:\n{base_analysis}"
        ]

        critiques = []

        for p in prompts:
            r = self.llm.generate(p)
            if r:
                critiques.append(r)

        return self.judge.judge(
            question,
            base_analysis,
            '\n\n'.join(critiques)
        )
