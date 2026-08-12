from pathlib import Path
from mind_trader.app.audits.operational_readme import build_operational_readme, save_operational_readme

def test_operational_readme_contains_blocks():
    r=build_operational_readme(194)
    assert "Production: BLOCKED" in r
    assert "Live: FORBIDDEN" in r
    assert "Edge claim: NONE" in r
    assert "paper_research_cli" in r

def test_save_operational_readme(tmp_path):
    p=save_operational_readme(str(tmp_path/"README.md"),194)
    assert Path(p).exists()
