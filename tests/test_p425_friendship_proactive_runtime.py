from app.friendship.proactive_scheduler import plan_checkin
from app.friendship.friendship_profile import default_profile

def test_friendship_proactive_runtime_acceptance():
    profile = default_profile("test-user")
    profile["name"] = "Roberto"

    out = plan_checkin(profile, {})
    assert out["send"] is True
    assert out["reason"] == "OK"
    assert "message" in out
    assert "Roberto" in out["message"]

def test_friendship_respects_opt_out_and_daily_limit():
    profile = default_profile("test-user")

    opt = profile.copy()
    opt["opt_out"] = True
    assert plan_checkin(opt, {}) == {"send": False, "reason": "OPT_OUT"}

    limit = profile.copy()
    limit["proactive_sent_today"] = 99
    limit["daily_limit"] = 1
    assert plan_checkin(limit, {}) == {"send": False, "reason": "DAILY_LIMIT"}
