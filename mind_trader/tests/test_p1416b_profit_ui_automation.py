from app.p1416b_profit_ui_automation.runner import run, SCRIPT

def test_p1416b_generates_ui_runner():
    m = run()
    assert m["STATUS"] == "P14.16B_PROFIT_UI_AUTOMATION_HARNESS_IMPLEMENTED"
    assert m["REAL_ORDERS"] == "FORBIDDEN"
    assert m["EDGE"] == "NOT_PROVEN"
    assert SCRIPT.exists()

def test_p1416b_script_uses_clipboard_and_screenshot():
    run()
    s = SCRIPT.read_text(encoding="utf-8")
    assert "Set-Clipboard" in s
    assert "SendKeys" in s
    assert "Save-Screenshot" in s
    assert "F9" in s
