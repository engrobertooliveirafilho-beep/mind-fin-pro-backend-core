from app.modules.usde_core.supabase_live_hook import USDESupabaseLiveHook

def test_supabase_live_hook():
    r=USDESupabaseLiveHook().observe_memory_event(
        "scientific_memory",
        {"status":"ok"}
    )

    assert r["memory"]["status"]=="UPSERTED"
    assert "hypothesis" in r["observation"]
    assert "experiment" in r["observation"]
    assert "evidence" in r["observation"]
    assert "decision" in r["observation"]
