import json
from pathlib import Path

def load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return {}

m = load("reports/P1501_EDGE_EVOLUTION_LIVE_MONITOR/latest_edge_evolution_monitor.json")
d = load("reports/P1502_DELTA_DAILY_EVOLUTION_MONITOR/latest_delta_report.json")

print("\n======================================================")
print(" MIND TRADER — EVOLUTION AUDIT")
print("======================================================")
print("\nESTADO ATUAL")
print("------------")
print(f"Health:                    {m.get('HEALTH')}")
print(f"Estratégias Geradas:       {m.get('AUTO_STRATEGIES_GENERATED_TODAY')}")
print(f"Backtests Executados:      {m.get('BACKTESTS_EXECUTED_TODAY')}")
print(f"Edges Promovidos:          {m.get('EDGES_PROMOTED_TODAY')}")
print(f"Top10:                     {m.get('TOP10')}")
print(f"Alocados:                  {m.get('ALLOCATED_EDGES')}")
print("\nEVOLUÇÃO DESDE O ÚLTIMO CICLO")
print("-----------------------------")
print(f"Novos Inputs Web:          {d.get('DELTA_WEB_INPUTS',0)}")
print(f"Novas Estratégias:         {d.get('DELTA_STRATEGIES_GENERATED',0)}")
print(f"Novos Backtests:           {d.get('DELTA_BACKTESTS',0)}")
print(f"Novos Candidatos:          {d.get('DELTA_BACKTEST_CANDIDATES',0)}")
print(f"Novos Walk Forward:        {d.get('DELTA_WALK_FORWARD',0)}")
print(f"Novos Monte Carlo:         {d.get('DELTA_MONTE_CARLO',0)}")
print(f"Novos Edges Promovidos:    {d.get('DELTA_PROMOTED_EDGES',0)}")

evolved = any([
    d.get("DELTA_WEB_INPUTS",0) > 0,
    d.get("DELTA_STRATEGIES_GENERATED",0) > 0,
    d.get("DELTA_BACKTESTS",0) > 0,
    d.get("DELTA_PROMOTED_EDGES",0) > 0
])

print("\nCONCLUSÃO")
print("---------")
print("STATUS: EVOLUINDO" if evolved else "STATUS: SEM EVOLUÇÃO DETECTADA")
print("======================================================\n")
