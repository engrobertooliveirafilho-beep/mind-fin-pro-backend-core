from app.p1412_ntsl_template_ladder.runner import run, EXPORT_DIR, TEMPLATES

def test_p1412_generates_all_templates():
    m = run()
    assert m["STATUS"] == "P14.12_NTSL_TEMPLATE_LADDER_IMPLEMENTED"
    assert m["REAL_ORDERS"] == "FORBIDDEN"
    assert m["EDGE"] == "NOT_PROVEN"
    for name in TEMPLATES:
        assert (EXPORT_DIR / f"{name}.nts").exists()

def test_p1412_templates_have_progressive_logic():
    run()
    assert "begin" in (EXPORT_DIR / "p1412_l1_empty.nts").read_text(encoding="utf-8")
    assert "BuyAtMarket" in (EXPORT_DIR / "p1412_l2_close_open_logic.nts").read_text(encoding="utf-8")
    assert "Close[1]" in (EXPORT_DIR / "p1412_l3_directional_if_only.nts").read_text(encoding="utf-8")
    assert "Media(9, Close)" in (EXPORT_DIR / "p1412_l4_single_media.nts").read_text(encoding="utf-8")
    assert "fastMA" in (EXPORT_DIR / "p1412_l5_dual_media.nts").read_text(encoding="utf-8")
