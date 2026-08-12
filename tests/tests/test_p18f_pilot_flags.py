from app.p18_conversational_execution.pilot_flags import load_flags, validate_flags

def test_p18f_flags_safe_defaults():
    flags = load_flags()
    assert validate_flags(flags)
    assert flags.ENABLE_INTERNAL_PILOT is False
    assert flags.ENABLE_WHATSAPP_OVERRIDE is False
    assert flags.ENABLE_PRODUCTION_ACTIVATION is False
