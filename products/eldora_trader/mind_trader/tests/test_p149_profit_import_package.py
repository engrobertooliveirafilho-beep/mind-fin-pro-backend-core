from pathlib import Path
from app.p149_profit_import_package.engine import build_package, run, DEST

def test_p149_build_package():
    items=build_package(limit=5)
    assert isinstance(items,list)

def test_p149_manifest():
    m=run()
    assert m["STATUS"]=="P14.9_PROFIT_IMPORT_PACKAGE_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True

def test_p149_package_dir_exists():
    run()
    assert Path(DEST).exists()
