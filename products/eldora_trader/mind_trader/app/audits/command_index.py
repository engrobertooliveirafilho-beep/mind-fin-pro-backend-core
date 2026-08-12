from pathlib import Path

COMMANDS = {
    "test_all": "$env:PYTHONPATH=(Get-Location).Path; pytest .\\mind_trader\\tests -q",
    "status": "$env:PYTHONPATH=(Get-Location).Path; python -m mind_trader.app.cli.status_cli --tests-passed 208",
    "final_audit": "$env:PYTHONPATH=(Get-Location).Path; python -m mind_trader.app.cli.final_audit_cli --tests-passed 208",
    "paper_research": "$env:PYTHONPATH=(Get-Location).Path; python -m mind_trader.app.cli.paper_research_cli --data-folder .\\mind_trader\\incoming_data --symbol TEST --timeframe 1m --db-path .\\mind_trader\\data\\market.sqlite --ftmo-config .\\mind_trader\\config\\ftmo_ruleset.json --limit 10"
}

def build_command_index(tests_passed=208):
    lines=[
        "# P8.75 Command Index",
        "",
        f"Tests passed: {tests_passed}",
        "",
        "Production: BLOCKED",
        "Live: FORBIDDEN",
        "Edge claim: NONE",
        "",
    ]
    for name,cmd in COMMANDS.items():
        lines += [f"## {name}", "", "```powershell", cmd, "```", ""]
    return "\n".join(lines)

def save_command_index(path="mind_trader/reports/P8.75_command_index.md",tests_passed=208):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    content=build_command_index(tests_passed)
    Path(path).write_text(content,encoding="utf-8")
    return path
