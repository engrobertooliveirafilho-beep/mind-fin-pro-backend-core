import copy
import pytest
from app.p9_genome_explosion_engine.engine import generate_genomes, run, gid

def test_p92_generate_10000_genomes_with_consistent_phenotype_ids():
    genomes=generate_genomes(10000)
    assert len(genomes)==10000
    assert all(g["genome_id"]==gid(g) for g in genomes)
    assert len({g["genome_id"] for g in genomes})==len({gid(g) for g in genomes})

def test_p92_identity_does_not_depend_on_generation_index():
    genome=generate_genomes(1)[0]
    clone=copy.deepcopy(genome)
    clone["index"] += 500
    assert gid(genome)==gid(clone)

def test_p92_identity_changes_when_strategy_parameter_changes():
    genome=generate_genomes(1)[0]
    clone=copy.deepcopy(genome)
    clone["fast"] = 999
    assert gid(genome)!=gid(clone)

def test_p92_contains_safety_constraints():
    genome=generate_genomes(100)[0]
    assert genome["live_allowed"] is False
    assert genome["promotion_allowed"] is False
    assert "risk_model" in genome and "regime_filter" in genome

def test_p92_manifest_reports_candidate_not_certified():
    manifest=run(1000)
    assert manifest["STATUS"]=="P9.2_GENOME_CANDIDATES_GENERATED_UNVALIDATED"
    assert manifest["CANDIDATE_ONLY"] is True
    assert manifest["BACKTEST_REQUIRED"] is True
    assert manifest["PROMOTION_ALLOWED"] is False
