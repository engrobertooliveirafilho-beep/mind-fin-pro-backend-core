import importlib

print("IMPORT_APP_MAIN_BEGIN")
from app.main import app
print("APP_IMPORT_OK", type(app))

try:
    fb = importlib.import_module("app.runtime.forensic_bootstrap")
    print("FORENSIC_BOOTSTRAP_IMPORT_OK")
    if hasattr(fb, "install_forensic_bootstrap"):
        print("INSTALL_1", fb.install_forensic_bootstrap())
        print("INSTALL_2", fb.install_forensic_bootstrap())
except Exception as e:
    print("FORENSIC_BOOTSTRAP_ERROR", type(e).__name__, str(e))
