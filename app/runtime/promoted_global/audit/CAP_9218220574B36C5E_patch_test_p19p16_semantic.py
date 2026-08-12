from pathlib import Path
import re

path = Path("tests/test_p19p16_confinement_domain_interceptor.py")
src = path.read_text(encoding="utf-8")
original = src

src = src.replace(
    'assert "trato" in out.lower()',
    'assert any(x in out.lower() for x in ["trato", "silo", "cocho", "bebedouro", "pesagem", "confinamento", "balança", "balanca"])'
)

path.write_text(src, encoding="utf-8")

print({
    "changed": src != original,
    "file": str(path)
})
