from app.runtime.universal_contextual_continuity_engine import ucce_shadow_evaluate
def run_ucce_shadow(sender_id,inbound_message,live_reply,state=None):
    try:return ucce_shadow_evaluate(sender_id,inbound_message,state)
    except Exception as e:return {"classification":"ERROR","reply":live_reply,"error":str(e)}
