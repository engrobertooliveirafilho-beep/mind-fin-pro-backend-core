from pathlib import Path
from mind_trader.app.dna.trader_dna_authority import create_dna_atom, validate_dna_atom, save_dna_atoms

def atom():
    return create_dna_atom(
        "absorption_after_sweep",
        "liquidity",
        context="liquidity sweep with failed continuation",
        trigger="close back inside range",
        invalidation="new low after absorption",
        target="opposite liquidity pool",
        risk="fixed fractional stop below sweep",
        success_conditions=["volume absorption","regime not high panic"]
    )

def test_create_valid_dna_atom():
    a=atom()
    assert a["valid"] is True
    assert len(a["atom_id"])==24
    assert a["production"]=="BLOCKED"

def test_validate_dna_atom_ok():
    r=validate_dna_atom(atom())
    assert r["decision"]=="DNA_ATOM_OK"
    assert r["edge_claim"]=="NONE"

def test_invalid_atom_blocks():
    a=create_dna_atom("bad","liquidity",context="x")
    r=validate_dna_atom(a)
    assert r["decision"]=="DNA_ATOM_BLOCKED"
    assert "trigger" in r["missing"]

def test_save_dna_atoms(tmp_path):
    p=save_dna_atoms([atom()],str(tmp_path/"atoms.json"))
    assert Path(p).exists()


def test_invalid_atom_field_types():
    for key, value in (("context", " "), ("trigger", 42), ("risk", []), ("success_conditions", []), ("success_conditions", [" "]), ("success_conditions", [None])):
        a = atom()
        a[key] = value
        assert validate_dna_atom(a)["valid"] is False
    assert validate_dna_atom(None)["valid"] is False


def test_invalid_batch_preserves_dna(tmp_path):
    import pytest
    p = tmp_path / "atoms.json"
    save_dna_atoms([atom()], str(p))
    before = p.read_bytes()
    invalid = dict(atom(), success_conditions=[])
    nonfinite = dict(atom(), extra=float("nan"))
    for batch in ([atom(), invalid], [nonfinite], None):
        with pytest.raises(ValueError):
            save_dna_atoms(batch, str(p))
        assert p.read_bytes() == before
