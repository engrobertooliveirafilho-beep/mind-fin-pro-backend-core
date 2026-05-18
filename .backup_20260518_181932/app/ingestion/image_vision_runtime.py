import os
import base64
from openai import OpenAI
from app.vision.domain_router import VisionDomainRouter

class ImageVisionRuntime:

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.router = VisionDomainRouter()

    def analyze(self, image_url=None, local_path=None, user_message=""):

        if local_path:
            with open(local_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            image_payload = f"data:image/jpeg;base64,{encoded}"
        else:
            image_payload = image_url

        domain = self.router.detect(user_message=user_message)
        prompt = self.router.prompt_for(domain)

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
            max_tokens=1300
        )

        return response.choices[0].message.content
