"""R252: isolated tests of archived original sources; never import production modules."""
from __future__ import annotations
import importlib.util
import sys
import types
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1] / "r251_sources" / "app"

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def install_pkg(name):
    if name not in sys.modules:
        m = types.ModuleType(name)
        m.__path__ = []
        sys.modules[name] = m

@pytest.fixture
def originals(monkeypatch):
    for name in ("app", "app.agents"):
        install_pkg(name)
    base = ROOT / "agents"
    config = load("app.agents.multi_agent", base / "multi_agent.py")
    alternative = load("app.agents.multi_agent_system", base / "multi_agent_system.py")
    return config, alternative

def handlers(module, invalid=False):
    roles = module.MultiAgentRole
    msg = module.MultiAgentMessage
    def h(role):
        return lambda history: msg(role=role, content=f"{role.value}:{len(history)}")
    return dict(orchestrator=h(roles.RESEARCHER if invalid else roles.ORCHESTRATOR),
                researcher=h(roles.RESEARCHER),
                toolmaster=h(roles.TOOLMASTER),
                summarizer=h(roles.SUMMARIZER))

def test_original_multi_agent_validates_role(originals):
    canonical, _ = originals
    system = canonical.MultiAgentSystem(**handlers(canonical, invalid=True))
    with pytest.raises(ValueError):
        system.run("test")

def test_alternative_missing_role_validation(originals):
    _, alternative = originals
    system = alternative.MultiAgentSystem(**handlers(alternative, invalid=True))
    history = system.run("test")
    assert history[1].role == alternative.MultiAgentRole.RESEARCHER

@pytest.mark.parametrize("rounds", [1, 2, 3])
def test_original_multi_agent_rounds(originals, rounds):
    canonical, _ = originals
    system = canonical.MultiAgentSystem(**handlers(canonical), config=canonical.MultiAgentConfig(max_rounds=rounds))
    history = system.run("test")
    assert len(history) == 1 + 4 * rounds

def test_profile_router_dependencies_present():
    assert (ROOT / "mind" / "agent_profiles.py").is_file()
    assert (ROOT / "mind" / "orchestrator.py").is_file()
    assert (ROOT / "mind" / "agent_router.py").is_file()
