from app.p9_research_command_center.engine import build_dashboard, DASHBOARDS

def test_p97_dashboard_sections_and_blocked_rankings():
    dashboard = build_dashboard()
    for section in DASHBOARDS:
        assert section in dashboard
    assert dashboard["status"] == "P9.7_BLOCKED_UPSTREAM_EVIDENCE_NOT_CERTIFIED"
    assert dashboard["top_genomes"] == []
    assert dashboard["top_paper_candidates"] == []
    assert dashboard["top_robustness"] == []
    assert dashboard["export_ready"] is False

def test_p97_blocks_real_promotion():
    dashboard = build_dashboard()
    assert dashboard["live"] == "FORBIDDEN"
    assert dashboard["real_broker"] == "DISABLED"
    assert dashboard["promotion_allowed"] is False
