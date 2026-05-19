from __future__ import annotations
import uuid,time,json
from app.runtime.duplicate_response_guard import should_block_duplicate
try:
    from app.humanization.humanization_runtime import humanize_response
except Exception:
    def humanize_response(user_message, raw_answer, context=None):
        return raw_answer
from app.humanization.universal_recovery_runtime import enforce_no_identity_in_normal_chat
from app.humanization.multi_message_reply_runtime import split_human_reply

def dispatch_single_runtime(sender_id:str,user_message:str,raw_answer:str,module:str="eldora_primary_runtime",function:str="eldora_primary_runtime_reply"):
    trace_id=str(uuid.uuid4())

    answer=humanize_response(user_message,raw_answer,{})
    answer=enforce_no_identity_in_normal_chat(user_message,answer)

    duplicate=should_block_duplicate(sender_id,answer)

    trace={
        "trace_id":trace_id,
        "sender_id":sender_id,
        "user_message":user_message,
        "runtime_origin":"single_runtime_dispatcher",
        "module":module,
        "function":function,
        "response_preview":(answer or "")[:180],
        "identity_leak":"eu sou a eldora" in (answer or "").lower(),
        "duplicate_risk":duplicate
    }

    print("[WHATSAPP_TRACE]",json.dumps(trace,ensure_ascii=False))
    print("[MODULE_ORIGIN]",module,function)

    if duplicate:
        print("[DUPLICATE_BLOCKED]",trace_id)
        return ""

    msgs=split_human_reply(answer,{})
    return "\n\n".join(msgs[:4])
