from app.runtime.cognitive_collision_registry import CognitiveCollisionRegistry

def test_collision_registry():
    reg = CognitiveCollisionRegistry()

    reg.register("A", ["memory","social"])
    reg.register("B", ["memory"])

    collisions = reg.get_collisions()

    assert "memory" in collisions
