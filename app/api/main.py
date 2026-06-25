from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "system": "eldora"}

@app.post("/orchestrator")
def orchestrator(payload: dict):
    return {
        "status": "received",
        "route": "gpu_or_runpod",
        "input": payload
    }

@app.post("/runpod/echo")
def runpod_echo(payload: dict):
    return {
        "status": "runpod_connected_mock",
        "payload": payload
    }
