from app.medical_swarm.personas import MEDICAL_PERSONAS
from app.multi_llm.provider_runtime import ProviderRuntime

class MedicalSwarmRuntime:

    def __init__(self):
        self.runtime=ProviderRuntime()

    def simulate(self,topic):

        outputs=[]

        for p in MEDICAL_PERSONAS:

            try:

                prompt=f"""
Você está simulando:
{p['name']}

País:
{p['country']}

Instituição:
{p['institution']}

Especialidade:
{p['specialty']}

Estilo:
{p['style']}

RESPONDA EM PORTUGUÊS.

Tema:
{topic}

Explique:
- visão clínica
- raciocínio
- riscos
- tratamento
- melhores práticas
"""

                result=self.runtime.execute(
                    p["provider"],
                    prompt
                )

                outputs.append({
                    "persona":p["name"],
                    "provider":p["provider"],
                    "response":result
                })

            except Exception as e:

                outputs.append({
                    "persona":p["name"],
                    "provider":p["provider"],
                    "error":str(e)
                })

        return {
            "status":"MEDICAL_SWARM_OPERATIONAL",
            "topic":topic,
            "agents":len(outputs),
            "outputs":outputs
        }
