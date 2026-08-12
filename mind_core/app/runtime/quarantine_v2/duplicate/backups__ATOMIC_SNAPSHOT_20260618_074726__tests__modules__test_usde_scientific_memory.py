from app.modules.usde_core.scientific_memory import ScientificMemory
import shutil
from pathlib import Path

def test_scientific_memory_store():
    root="_evidence/P4.46X_USDE_CORE/test_memory"
    shutil.rmtree(root, ignore_errors=True)

    m=ScientificMemory(root)

    r=m.store(
        "hypothesis",
        {"name":"test"}
    )

    assert "memory_id" in r

def test_scientific_memory_query():
    root="_evidence/P4.46X_USDE_CORE/test_memory_query"
    shutil.rmtree(root, ignore_errors=True)

    m=ScientificMemory(root)

    m.store("a",{"x":1})
    m.store("b",{"x":2})

    r=m.query("a")

    assert len(r)==1
