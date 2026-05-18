from app.human.multi_llm_runtime import MultiLLMRuntime

class ConsensusJudge:

    def __init__(self):
        self.llm = MultiLLMRuntime()

    def judge(self, question, base_analysis, critiques):

        prompt = f"""
Você é um juiz de consenso multimodal da NEURA.

Pergunta:
{question}

Análise principal:
{base_analysis}

Análises complementares:
{critiques}

Monte uma resposta:
- profunda
- útil
- honesta
- contextual
- sem inventar certezas
"""

        result = self.llm.generate(prompt)

        if result:
            return result

        return base_analysis
