from app.modules.usde_core.experiment_queue import ExperimentQueue

def test_experiment_queue():
    q=ExperimentQueue()
    r=q.enqueue({"name":"test"})

    assert "job_id" in r
    assert r["status"]=="QUEUED"
    assert q.count() >= 1
