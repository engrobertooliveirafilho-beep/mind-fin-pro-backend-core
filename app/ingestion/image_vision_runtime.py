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

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analise esta imagem enviada no WhatsApp. Descreva objetivamente o que aparece e destaque detalhes úteis."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_payload
                            }
                        }
                    ]
                }
            ],
            max_tokens=700
        )

        return response.choices[0].message.content
