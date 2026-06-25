from dataclasses import dataclass

@dataclass
class P18PilotFlags:
    ENABLE_CONVERSATIONAL_EXECUTION_SHADOW: bool = True
    ENABLE_INTERNAL_PILOT: bool = False
    ENABLE_RUNTIME_RESPONSE_SELECTION: bool = False
    ENABLE_WHATSAPP_OVERRIDE: bool = False
    ENABLE_PRODUCTION_ACTIVATION: bool = False

def load_flags():
    return P18PilotFlags()

def validate_flags(flags: P18PilotFlags):
    assert flags.ENABLE_CONVERSATIONAL_EXECUTION_SHADOW is True
    assert flags.ENABLE_INTERNAL_PILOT is False
    assert flags.ENABLE_RUNTIME_RESPONSE_SELECTION is False
    assert flags.ENABLE_WHATSAPP_OVERRIDE is False
    assert flags.ENABLE_PRODUCTION_ACTIVATION is False
    return True
