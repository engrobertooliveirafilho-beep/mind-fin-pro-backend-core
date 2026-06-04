
from app.runtime.subject_alias_engine import subject_alias

def test_corolla():
    assert subject_alias("quero comprar um Corolla")=="Corolla"

def test_ram():
    assert subject_alias("quero comprar uma RAM 2500 ano 2026")=="RAM 2500 ano 2026"

def test_r44():
    assert subject_alias("quero comprar um helicóptero Robinson R44")=="helicóptero Robinson R44"

def test_confinamento():
    assert subject_alias("quero montar um confinamento para 200 bois")=="confinamento para 200 bois"
