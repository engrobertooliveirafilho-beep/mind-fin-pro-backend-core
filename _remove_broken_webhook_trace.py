from pathlib import Path

p=Path("app/main.py")
lines=p.read_text(encoding="utf-8").splitlines()

# remove linhas 415-422 exibidas no inspect: FIX11K_TRACE_ACTIVE quebrado
start=414  # zero-based linha 415
end=422    # exclusive linha 422

fixed=lines[:start]+lines[end:]
p.write_text("\n".join(fixed)+"\n", encoding="utf-8")

print("BROKEN_WEBHOOK_TRACE_BLOCK_REMOVED")
