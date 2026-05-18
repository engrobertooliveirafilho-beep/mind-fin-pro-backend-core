import os
import time
import requests

class OpenAIProvider:

    def __init__(self):
        self.api_key=os.getenv("OPENAI_API_KEY","")

    def health(self):
        return bool(self.api_key)

    def chat(self,message):

        t0=time.time()

        r=requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization":f"Bearer {self.api_key}",
                "Content-Type":"application/json"
            },
            json={
                "model":"gpt-4.1-mini",
                "messages":[{"role":"user","content":message}],
                "temperature":0.3
            },
            timeout=45
        )

        dt=round((time.time()-t0)*1000)

        data=r.json()

        return {
            "provider":"openai",
            "latency_ms":dt,
            "response":data["choices"][0]["message"]["content"]
        }
