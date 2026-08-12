from app.modules.usde_core.supabase_scientific_memory import SupabaseScientificMemory

def test_supabase_scientific_memory():
    m=SupabaseScientificMemory()
    r=m.upsert("scientific_memory",{"status":"ok"})

    assert r["status"]=="UPSERTED"
    assert m.count() >= 1
