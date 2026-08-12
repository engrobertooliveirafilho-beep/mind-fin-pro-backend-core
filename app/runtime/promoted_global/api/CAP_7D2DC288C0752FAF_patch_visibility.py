from pathlib import Path

p = Path("app/api/whatsapp.py")
s = p.read_text(encoding="utf-8")

old = '''except Exception:
    _p19p28_is_fitness = None'''

new = '''except Exception as _p19p28_import_error:
    try:
        from pathlib import Path as _P19P28Path
        _P19P28Path("_evidence_p19p28_import_error.txt").write_text(str(_p19p28_import_error), encoding="utf-8")
    except Exception:
        pass
    _p19p28_is_fitness = None'''

if old in s and "_evidence_p19p28_import_error.txt" not in s:
    s = s.replace(old, new, 1)

old2 = '''    except Exception:
        pass

    _p19h3_text = str(inbound_text or "").lower().strip()'''

new2 = '''    except Exception as _p19p28_router_error:
        try:
            from pathlib import Path as _P19P28Path
            _P19P28Path("_evidence_p19p28_router_error.txt").write_text(str(_p19p28_router_error), encoding="utf-8")
        except Exception:
            pass

    _p19h3_text = str(inbound_text or "").lower().strip()'''

if old2 in s and "_evidence_p19p28_router_error.txt" not in s:
    s = s.replace(old2, new2, 1)

p.write_text(s, encoding="utf-8")
print("P19P28O_VISIBILITY_PATCH_OK")
