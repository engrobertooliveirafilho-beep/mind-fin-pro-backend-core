from pathlib import Path

evid = Path(__file__).parent
targets = [
    "07_hit_FTMO.txt",
    "07_hit_checklist_FTMO.txt",
    "07_hit_continue.txt",
    "07_hit_prossiga.txt",
    "07_hit_quais.txt",
    "08_main_execution_order.txt",
    "09_whatsapp_execution_order.txt",
    "10_probe_router_called.txt",
    "11_direct_context_router_test.txt",
]

for name in targets:
    p = evid / name
    print("\n====", name, "====")
    if p.exists():
        txt = p.read_text(encoding="utf-8", errors="ignore")
        lines = txt.splitlines()
        for line in lines[:220]:
            print(line)
    else:
        print("MISSING")
