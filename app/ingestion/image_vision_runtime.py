import os
import base64
from openai import OpenAI

class ImageVisionRuntime:

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def analyze(self, image_url=None, local_path=None):

        if local_path:
            with open(local_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            image_payload = f"data:image/jpeg;base64,{encoded}"
        else:
            image_payload = image_url

        prompt = """
Faça uma análise visual avançada e honesta da imagem.

Obrigatório:
1. Descreva o que aparece.
2. Se houver carro, estime marca/modelo provável, geração ou faixa de ano, mas diga o grau de incerteza.
3. Analise estado externo visível: pintura, rodas, pneus, faróis, posição, conservação.
4. Se houver plantas/flores, estime o tipo provável e explique o limite da certeza.
5. Destaque elementos do ambiente.
6. Diga claramente o que NÃO dá para confirmar pela imagem.
7. Não invente certeza. Use "parece", "provavelmente", "não é possível confirmar".
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_payload}}
                    ]
                }
            ],
            max_tokens=1200
        )

        return response.choices[0].message.content
