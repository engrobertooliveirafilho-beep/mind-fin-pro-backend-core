from pathlib import Path
from mind_trader.app.genomes.strategy_genome import make_genome, validate_genome, generate_strategy_genomes, rank_genomes_by_validation, save_genomes

def test_make_genome_has_deterministic_hash():
    a=make_genome("SMA_CROSS","TEST","1m","TREND_UP",{"fast":9,"slow":21})
    b=make_genome("SMA_CROSS","TEST","1m","TREND_UP",{"slow":21,"fast":9})
    assert a["genome_id"]==b["genome_id"]

def test_blocks_undefined_regime():
    g=make_genome("SMA_CROSS","TEST","1m","UNDEFINED",{"fast":9,"slow":21})
    ok,reason=validate_genome(g)
    assert ok is False
    assert reason=="REGIME_NOT_ALLOWED_OR_UNDEFINED"

def test_valid_genome_ok():
    g=make_genome("BREAKOUT","TEST","1m","EXPANSION_HIGH_VOL",{"lookback":20})
    assert validate_genome(g)[0] is True

def test_generate_strategy_genomes_real_count():
    gs=generate_strategy_genomes(symbols=("WIN","WDO"),timeframes=("1m","5m"))
    ids=[g["genome_id"] for g in gs]
    assert len(gs)>40
    assert len(ids)==len(set(ids))

def test_all_generated_genomes_validate():
    gs=generate_strategy_genomes()
    assert all(validate_genome(g)[0] for g in gs)

def test_rank_genomes_research_only():
    gs=generate_strategy_genomes()
    report={gs[0]["genome_id"]:{"classification":"RESEARCH_CANDIDATE","out_of_sample":{"expectancy":1,"profit_factor":1.5,"max_drawdown":5}}}
    ranked=rank_genomes_by_validation(gs,report)
    assert ranked[0]["genome_id"]==gs[0]["genome_id"]
    assert ranked[0]["production"]=="BLOCKED"

def test_save_genomes(tmp_path):
    out=save_genomes(generate_strategy_genomes(),str(tmp_path/"genomes.json"))
    assert Path(out).exists()
