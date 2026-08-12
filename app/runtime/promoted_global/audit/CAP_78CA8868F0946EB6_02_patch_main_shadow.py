from pathlib import Path

p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

needle = '''                try:
                    from app.companionship.p19p31_p19p36_companion_runtime import compose_reply as _p19p31_compose_reply
                    reply = _p19p31_compose_reply(sender, body, ctxu, reply)
                except Exception:
                    pass
'''

replacement = '''                try:
                    from app.companionship.safe_recovery_adapter import collect_recovered_context as _p19p36h_collect_recovered_context
                    from app.companionship.safe_recovery_adapter import enrich_reply_shadow as _p19p36h_enrich_reply_shadow
                    from app.companionship.safe_recovery_adapter import record_shadow_telemetry as _p19p36h_record_shadow_telemetry
                    ctxu = _p19p36h_collect_recovered_context(sender, body, ctxu)
                    reply = _p19p36h_enrich_reply_shadow(sender, body, ctxu, reply)
                    _p19p36h_record_shadow_telemetry(sender, body, ctxu, reply)
                except Exception:
                    pass

                try:
                    from app.companionship.p19p31_p19p36_companion_runtime import compose_reply as _p19p31_compose_reply
                    reply = _p19p31_compose_reply(sender, body, ctxu, reply)
                except Exception:
                    pass
'''

if "p19p36h_collect_recovered_context" not in s:
    if needle not in s:
        raise SystemExit("COMPANION_ENRICHMENT_BLOCK_NOT_FOUND")
    s = s.replace(needle, replacement, 1)

p.write_text(s, encoding="utf-8")
print("P19P36H_MAIN_SHADOW_WIRING_OK")
