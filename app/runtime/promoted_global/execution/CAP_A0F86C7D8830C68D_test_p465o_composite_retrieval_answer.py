from pathlib import Path
import os

def load_env():
    for raw in Path(".env").read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env()

from app.runtime.cognitive_pipeline import run_cognitive_pipeline


def test_p465o_retrieval_answers_name():
    out = run_cognitive_pipeline("whatsapp:+5519996166906", "Use retrieval e responda: qual é meu nome?")
    assert out["answer"] == "Seu nome é Roberto."
    assert out["retrieval"]["used"] is True


def test_p465o_retrieval_answers_study():
    out = run_cognitive_pipeline("whatsapp:+5519996166906", "Use retrieval e responda: o que estou estudando?")
    assert out["answer"] == "Você está estudando matemática."
    assert out["retrieval"]["used"] is True


def test_p465o_retrieval_answers_composite():
    out = run_cognitive_pipeline("whatsapp:+5519996166906", "Use retrieval e responda: qual é meu nome e o que estou estudando?")
    assert out["answer"] == "Seu nome é Roberto e você está estudando matemática."
    assert out["retrieval"]["used"] is True
