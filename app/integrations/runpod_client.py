import os
import time
import requests

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY", "")
RUNPOD_ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID", "")

class RunPodClient:
    def __init__(self):
        if not RUNPOD_API_KEY:
            raise RuntimeError("RUNPOD_API_KEY missing")
        if not RUNPOD_ENDPOINT_ID:
            raise RuntimeError("RUNPOD_ENDPOINT_ID missing")

        self.base_url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}"
        self.headers = {
            "Authorization": f"Bearer {RUNPOD_API_KEY}",
            "Content-Type": "application/json",
        }

    def run(self, payload: dict, timeout_seconds: int = 120):
        response = requests.post(
            f"{self.base_url}/run",
            headers=self.headers,
            json={"input": payload},
            timeout=30,
        )
        response.raise_for_status()

        job = response.json()
        job_id = job["id"]

        start = time.time()

        while True:
            status_response = requests.get(
                f"{self.base_url}/status/{job_id}",
                headers=self.headers,
                timeout=30,
            )
            status_response.raise_for_status()

            status = status_response.json()

            if status.get("status") in ["COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"]:
                return status

            if time.time() - start > timeout_seconds:
                return {
                    "status": "CLIENT_TIMEOUT",
                    "job_id": job_id,
                    "message": "RunPod job polling timeout",
                }

            time.sleep(3)

    def health(self):
        return self.run({"task": "health"}, timeout_seconds=90)

    def echo(self, message: str):
        return self.run({"task": "echo", "message": message}, timeout_seconds=90)

    def generate_image(self, prompt: str):
        return self.run({"task": "generate_image", "prompt": prompt}, timeout_seconds=180)

    def transcribe_audio(self, audio_url: str):
        return self.run({"task": "transcribe_audio", "audio_url": audio_url}, timeout_seconds=180)
