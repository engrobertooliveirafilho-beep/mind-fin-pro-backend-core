from app.mcl.self_model.model import CivilizationSelfModel
from app.mcl.simulation.future import FutureStateSimulation
from app.mcl.governance.rewriter import GovernanceRewriter
from app.mcl.branching.branches import CivilizationBranching
from app.mcl.meta_memory.memory import MetaMemory

class MetaCivilization:
    def __init__(self):
        self.model = CivilizationSelfModel()
        self.simulation = FutureStateSimulation()
        self.governance = GovernanceRewriter()
        self.branching = CivilizationBranching()
        self.memory = MetaMemory()

    def evolve(self, system_state):
        model = self.model.build(system_state)
        futures = self.simulation.simulate(system_state)
        branches = self.branching.create_branch(system_state)
        self.memory.store_civilization_state(system_state)

        return {
            "self_model": model,
            "future_states": futures,
            "branches": branches
        }
