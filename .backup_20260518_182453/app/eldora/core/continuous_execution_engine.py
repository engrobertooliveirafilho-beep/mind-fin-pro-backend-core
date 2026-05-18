from datetime import datetime, timezone

EXECUTION_LOOPS=[]

def execute_loop(mission:str):
    item = {
        "mission":mission,
        "status":"running",
        "retry_strategy":"adaptive",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    EXECUTION_LOOPS.append(item)

    return {
        "status":"ok",
        "loop":item
    }

def loop_report():
    return {
        "status":"ok",
        "loops_total":len(EXECUTION_LOOPS),
        "loops":EXECUTION_LOOPS[-100:]
    }
