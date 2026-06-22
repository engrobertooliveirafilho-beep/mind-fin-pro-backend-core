from app.companionship.p19p52_capability_promotion_map import get_p19p52_promotion_map


def test_p19p52_promotion_map_contract():
    data = get_p19p52_promotion_map()

    assert data["program"] == "P19P52"
    assert data["mode"] == "SHADOW_PROMOTION_MAP"
    assert data["production_enabled"] is False
    assert data["runtime_mutation"] is False
    assert data["response_mutation"] is False
    assert len(data["priority_1"]) == 5
    assert len(data["priority_2"]) == 5
