import os
import requests
from openai import OpenAI

class MultiLLMRuntime:

    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK") or os.getenv("DEEPSEEK_API_KEY")
        self.mistral_key = os.getenv("MISTRAL") or os.getenv("MISTRAL_API_KEY")

    def _openai(self, prompt):
        if not self.openai_key:
            return None

        client = OpenAI(api_key=self.openai_key)

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Você é a NEURA, uma tutora cognitiva humana, direta e útil para estudantes via WhatsApp."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.55,
            max_tokens=700
        )

        return response.choices[0].message.content

    def _deepseek(self, prompt):
        if not self.deepseek_key:
            return None

        r = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {self.deepseek_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Você é a NEURA, tutora cognitiva para estudantes."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.55,
                "max_tokens": 700
            },
            timeout=18
        )

        if r.status_code >= 300:
            return None

        return r.json()["choices"][0]["message"]["content"]

    def _mistral(self, prompt):
        if not self.mistral_key:
            return None

        r = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.mistral_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-small-latest",
                "messages": [
                    {"role": "system", "content": "Você é a NEURA, tutora cognitiva para estudantes."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.55,
                "max_tokens": 700
            },
            timeout=18
        )

        if r.status_code >= 300:
            return None

        return r.json()["choices"][0]["message"]["content"]

    def generate(self, prompt):
        for provider in [self._openai, self._deepseek, self._mistral]:
            try:
                result = provider(prompt)
                if result and len(str(result).strip()) > 10:
                    return str(result).strip()
            except Exception:
                continue

        return None
