from pathlib import Path
from app.p12_cloud_export_verification_ledger.engine import verify_export

def test_p122_ledger_confirms_cloud_export():
    l=verify_export()
    assert l["CLOUD_EXPORT_CONFIRMED_BY_TERMINAL"] is True
    assert l["TRANSFERRED_FILES"]==6
    assert l["TRANSFER_STATUS"]=="100%"

def test_p122_blocks_live_and_real_broker():
    l=verify_export()
    assert l["LIVE"]=="FORBIDDEN"
    assert l["REAL_BROKER"]=="DISABLED"
    assert l["FTMO_REAL"]=="FORBIDDEN"

def test_p122_ledger_file_written():
    verify_export()
    assert Path("reports/P12.2_CLOUD_EXPORT_VERIFICATION_LEDGER/P12.2_cloud_export_verification_ledger.json").exists()
