from app.companionship.long_term_memory_real import consolidate_long_term_memory

def test_consolidates_memory(tmp_path):
    ctx={"p19p37a_digital_twin_real_shadow":{"profile":{"goals":["emagrecer"],"projects":["FTMO"],"constraints":["dor joelho"]}}}
    out=consolidate_long_term_memory("u", ctx, path=tmp_path/"m.json")
    assert "emagrecer" in out["memory"]["stable_goals"]
    assert "FTMO" in out["memory"]["stable_projects"]
