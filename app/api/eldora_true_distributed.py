from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.eldora.core.true_redis_runtime import publish_true_stream, true_stream_report
from app.eldora.core.distributed_worker_loop import run_worker_loop, worker_loop_report
from app.eldora.core.websocket_cognition import websocket_cognition_signal, websocket_report

router=APIRouter(prefix="/eldora/true-distributed", tags=["eldora-true-distributed"])

@router.post("/redis/publish")
async def redis_publish(stream:str="eldora.true.events", event:str="runtime_tick"):
    return publish_true_stream(stream,event)

@router.get("/redis/report")
async def redis_report(stream:str="eldora.true.events"):
    return true_stream_report(stream)

@router.post("/worker/loop")
async def worker_loop(worker_name:str="worker_alpha", cycles:int=1):
    return run_worker_loop(worker_name, cycles)

@router.get("/worker/report")
async def workers():
    return worker_loop_report()

@router.post("/websocket/signal")
async def ws_signal(channel:str="runtime", message:str="heartbeat"):
    return websocket_cognition_signal(channel,message)

@router.get("/websocket/report")
async def ws_report():
    return websocket_report()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data=await websocket.receive_text()
            websocket_cognition_signal("ws",data)
            await websocket.send_json({"status":"ok","echo":data})
    except WebSocketDisconnect:
        return
