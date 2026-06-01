from fastapi import APIRouter
from datetime import datetime
from random import random, choice

from app.golden_pipeline.memory_engine import memory_engine
from app.golden_pipeline.emotional_engine import emotional_engine
from app.golden_pipeline.reasoning_engine import reasoning_engine
from app.golden_pipeline.strategy_engine import strategy_engine
from app.golden_pipeline.decision_engine import decision_engine
from app.golden_pipeline.state_machine import state_machine
from app.golden_pipeline.behavior_engine import behavior_engine
from app.golden_pipeline.live_call_engine import live_call
from app.golden_pipeline.voice_director import director, VoiceUnavailable

router = APIRouter(prefix="/mind/golden/proactive", tags=["Golden Proactivity"])

def _ts():
    return datetime.utcnow().timestamp()

@router.get("/tick")
def proactive_tick():
    # probabilidade de iniciar ação espontânea
    trigger = random()

    # 1. checar memória e emoções (contexto)
    mem = memory_engine.snapshot()
    emo = emotional_engine.tick()["emotion"]

    # 2. caso haja gatilho → Golden age sem input externo
    if trigger > 0.4:
        reason = reasoning_engine.tick()
        strat = strategy_engine.tick()
        dec = decision_engine.tick()
    else:
        # fallback para idle ativo
        dec = {
            "gesture": "idle",
            "expression": emo,
            "intensity": 0.5,
            "text": "Chefão, estou em modo vigilante.",
        }
        reason = {"interpretation": "Aguardando estímulos."}
        strat = {"strategy_plan": ["observar", "analisar", "economizar energia"]}

    gesture = dec["gesture"]
    expression = dec["expression"]
    intensity = dec["intensity"]
    text = dec["text"]

    # 3. estado
    state_machine.transition(gesture)

    # 4. comportamento
    behavior = behavior_engine.tick()

    # 5. frame
    frame = live_call.frame()

    # 6. voz
    try:
        audio = director.synth_line(
            text=text,
            emotion=expression,
            intensity=intensity,
        )
    except Exception as e:
        audio = {"status": "voice_error", "detail": str(e)}

    # 7. armazenar na memória
    memory_engine.add_event("proactive_action", {
        "gesture": gesture,
        "expression": expression,
        "emotion": emo,
    })

    return {
        "status": "proactive_ok",
        "timestamp": _ts(),
        "trigger": trigger,
        "emotion": emo,
        "reasoning": reason,
        "strategy": strat,
        "decision": dec,
        "behavior": behavior,
        "frame": frame,
        "audio": audio,
        "memory_snapshot": mem,
    }
