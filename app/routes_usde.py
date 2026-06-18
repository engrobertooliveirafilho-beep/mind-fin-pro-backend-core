from fastapi import APIRouter
from pydantic import BaseModel
from app.modules.usde_core.usde_core import USDECore
from app.modules.usde_core.experiment_runner import ExperimentRunner

router = APIRouter(prefix="/usde", tags=["USDE"])

class USDERequest(BaseModel):
    events: list[dict]
    outdir: str = "tmp_usde_run"

@router.get("/status")
def usde_status():
    return {
        "module": "P4.46X_USDE_CORE",
        "status": "active",
        "red_team": "enabled",
        "scientific_ledger": "enabled"
    }

@router.post("/run")
def usde_run(req: USDERequest):
    return USDECore().run(req.events, req.outdir)

class USDEFileRequest(BaseModel):
    path: str
    hypothesis: str = "Hipótese experimental USDE"
    params: dict = {}

@router.post("/run-file")
def usde_run_file(req: USDEFileRequest):
    return ExperimentRunner().run_file(req.path, req.hypothesis, req.params)
