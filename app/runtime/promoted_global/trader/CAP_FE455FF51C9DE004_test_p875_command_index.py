from pathlib import Path
from mind_trader.app.audits.command_index import build_command_index, save_command_index, COMMANDS

def test_command_index_contains_commands():
    r=build_command_index(208)
    assert "test_all" in r
    assert "final_audit" in r
    assert "paper_research" in r
    assert "Production: BLOCKED" in r

def test_commands_defined():
    assert "status" in COMMANDS
    assert "paper_research" in COMMANDS

def test_save_command_index(tmp_path):
    p=save_command_index(str(tmp_path/"commands.md"),208)
    assert Path(p).exists()
