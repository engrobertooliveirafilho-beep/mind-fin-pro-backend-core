import os

class GroqProvider:

    def __init__(self):
        self.api_key=os.getenv("GroqCloud","")

    def health(self):
        return bool(self.api_key)

    def chat(self,message):

        return {
            "provider":"groq",
            "latency_ms":120,
            "response":"GROQ_FALLBACK_ACTIVE"
        }

