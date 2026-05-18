from datetime import datetime, timezone
import uuid

CHECKPOINTS = {}

def create_checkpoint(runtime_state: dict):
    checkpoint_id = str(uuid.uuid4())

    checkpoint = {
        "checkpoint_id": checkpoint_id,
        "runtime_state": runtime_state,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    CHECKPOINTS[checkpoint_id] = checkpoint
    return checkpoint

def checkpoint_report():
    return {
        "status": "ok",
        "checkpoints_total": len(CHECKPOINTS),
        "checkpoints": list(CHECKPOINTS.values())[-20:]
    }
