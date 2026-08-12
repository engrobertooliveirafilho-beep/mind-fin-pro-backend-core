from pathlib import Path
from app.p12_real_data_loading_cloud_export.engine import build_export_package

def test_p12_export_package_manifest():
    m=build_export_package()
    assert m["STATUS"]=="P12_REAL_DATA_LOADING_CLOUD_EXPORT_IMPLEMENTED"
    assert m["EXPORT_READY"] is True
    assert m["LIVE"]=="FORBIDDEN"

def test_p12_package_files_written():
    build_export_package()
    assert Path("reports/P12_REAL_DATA_LOADING_CLOUD_EXPORT/export_package/P12_export_manifest.json").exists()
    assert Path("reports/P12_REAL_DATA_LOADING_CLOUD_EXPORT/P12_manifest.json").exists()

def test_p12_cloud_upload_flag():
    m=build_export_package()
    assert m["CLOUD_UPLOAD_REQUIRED"] is True
    assert m["REAL_BROKER"]=="DISABLED"
