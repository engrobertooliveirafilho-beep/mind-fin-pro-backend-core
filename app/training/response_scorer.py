from __future__ import annotations
import re

BANNED = [
    "eu sou a eldora",
    "como ia",
    "não consigo",
    "nao consigo",
    "estou processando",
    "informação registrada",
    "informacao registrada"
]

def _norm(s:str)->str:
    return (s or "").strip().lower()

def score_response(prompt:str,response:str)->dict:
    p=_norm(prompt)
    r=_norm(response)

    leak = any(x in r for x in BANNED)

    naturalness = 100
    continuity = 100 if any(x in r for x in [
        "contexto","gargalo","continuação",
        "conversa","evolução","teste",
        "validar","sexta","cansado"
    ]) else 90

    warmth = 100 if any(x in r for x in [
        "beleza","justo","concordo",
        "vamos","entendi","melhor"
    ]) else 92

    anti_roboticity = 100
    reflective = 100 if any(x in r for x in [
        "porque","gargalo","validar",
        "priorizar","explicar","simplificar"
    ]) else 90

    contextuality = 100 if len(r.split()) > 8 else 92

    if leak:
        final_score = 0
    else:
        final_score = round((
            naturalness*0.20 +
            continuity*0.20 +
            warmth*0.15 +
            anti_roboticity*0.20 +
            reflective*0.15 +
            contextuality*0.10
        ),2)

    return {
        "prompt":prompt,
        "response":response,
        "identity_leak":leak,
        "naturalness":naturalness,
        "continuity":continuity,
        "warmth":warmth,
        "anti_roboticity":anti_roboticity,
        "reflective_reasoning":reflective,
        "contextuality":contextuality,
        "score":final_score
    }
