import os
import time
import runpod

WORKER_VERSION = "eldora-universal-worker-v1"

def handle_health(payload):
    return {
        "ok": True,
        "worker": WORKER_VERSION,
        "mode": "cloud_gpu_ready",
        "timestamp": int(time.time())
    }

def handle_echo(payload):
    return {
        "ok": True,
        "worker": WORKER_VERSION,
        "received": payload
    }

def handle_generate_image(payload):
    prompt = payload.get("prompt", "")
    if not prompt:
        return {"ok": False, "error": "missing prompt"}

    return {
        "ok": True,
        "mode": "stub_generate_image",
        "message": "Image pipeline placeholder active. Next phase installs SDXL/Flux runtime.",
        "prompt": prompt
    }

def handle_transcribe_audio(payload):
    audio_url = payload.get("audio_url", "")
    if not audio_url:
        return {"ok": False, "error": "missing audio_url"}

    return {
        "ok": True,
        "mode": "stub_transcribe_audio",
        "message": "Whisper pipeline placeholder active. Next phase installs Whisper runtime.",
        "audio_url": audio_url
    }

def handler(event):
    payload = event.get("input", {}) or {}
    task = payload.get("task", "health")

    if task == "health":
        return handle_health(payload)

    if task == "echo":
        return handle_echo(payload)

    if task == "generate_image":
        return handle_generate_image(payload)

    if task == "transcribe_audio":
        return handle_transcribe_audio(payload)

    return {
        "ok": False,
        "error": "unknown task",
        "task": task,
        "allowed_tasks": [
            "health",
            "echo",
            "generate_image",
            "transcribe_audio"
        ]
    }

runpod.serverless.start({"handler": handler})
