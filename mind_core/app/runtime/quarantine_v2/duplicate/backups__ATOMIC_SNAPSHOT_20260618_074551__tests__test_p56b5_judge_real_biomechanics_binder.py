from app.mind.p5_6b5_judge_real_biomechanics_binder import run_p56b5_judge_binder_healthcheck
from app.mind.p5_6b5_judge_real_biomechanics_binder.binder import JudgeRealBiomechanicsBinder

def test_healthcheck():
    assert run_p56b5_judge_binder_healthcheck()["status"]=="P5.6B5_JUDGE_BINDER_READY"

def test_score():
    b={"kick_score":100,"spin_score":75,"difficulty_score":100,"explosiveness_score":20,"buckoff_pressure_score":73}
    assert JudgeRealBiomechanicsBinder(url="https://x.supabase.co", key="fake").score(b) > 35
