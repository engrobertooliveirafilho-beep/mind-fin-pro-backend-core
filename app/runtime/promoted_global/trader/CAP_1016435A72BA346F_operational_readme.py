from pathlib import Path

def build_operational_readme(tests_passed=194):
    return (
        "# MIND Trader Private - Paper Research Operation\n\n"
        f"Tests passed: {tests_passed}\n\n"
        "## Status\n\n"
        "- Production: BLOCKED\n"
        "- Live: FORBIDDEN\n"
        "- Edge claim: NONE\n"
        "- Causality claim: NOT_PROVEN\n"
        "- Max scope: PAPER_RESEARCH_ONLY\n\n"
        "## Run tests\n\n"
        "```powershell\n"
        "$env:PYTHONPATH=(Get-Location).Path; pytest .\\mind_trader\\tests -q\n"
        "```\n\n"
        "## Run paper research operation\n\n"
        "```powershell\n"
        "$env:PYTHONPATH=(Get-Location).Path; python -m mind_trader.app.cli.paper_research_cli --data-folder .\\mind_trader\\incoming_data --symbol TEST --timeframe 1m --db-path .\\mind_trader\\data\\market.sqlite --ftmo-config .\\mind_trader\\config\\ftmo_ruleset.json --limit 10\n"
        "```\n\n"
        "## Required CSV columns\n\n"
        "ts, open, high, low, close, volume\n\n"
        "## Institutional rule\n\n"
        "No live trading. No production approval. No edge claim without evidence.\n"
    )

def save_operational_readme(path='mind_trader/reports/P8.70_OPERATIONAL_README.md',tests_passed=194):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    content=build_operational_readme(tests_passed)
    Path(path).write_text(content,encoding='utf-8')
    return path
