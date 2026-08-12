from app.p1416_import_autorun_reconciliation.engine import run, list_files, read_autorun_results

def test_p1416_lists_files():
    assert isinstance(list_files(__import__("pathlib").Path("tools"),"*.ps1"),list)

def test_p1416_reads_results():
    assert isinstance(read_autorun_results(),list)

def test_p1416_manifest():
    m=run()
    assert m["STATUS"]=="P14.16_IMPORT_AUTORUN_RECONCILIATION_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
