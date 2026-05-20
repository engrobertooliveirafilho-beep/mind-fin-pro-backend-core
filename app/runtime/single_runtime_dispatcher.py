from __future__ import annotations
import uuid,time,json
from app.runtime.duplicate_response_guard import should_block_duplicate
from app.humanization.universal_recovery_runtime import enforce_no_identity_in_normal_chat
from app.humanization.multi_message_reply_runtime import split_human_reply
from app.runtime.whatsapp_trace_sensor import new_trace,add_event,save_trace,sanitize_final_output
from app.telemetry.cloud_telemetry import log_event
from app.runtime.conversation_quality_guard import final_conversation_guard
try:
    from app.humanization.humanization_runtime import humanize_response
except Exception:
    def humanize_response(user_message, raw_answer, context=None):
        return raw_answer

def dispatch_single_runtime(sender_id:str,user_message:str,raw_answer:str,module:str="eldora_primary_runtime",function:str="eldora_primary_runtime_reply"):
    trace=new_trace(sender_id,user_message)
    add_event(trace,"input",module,function,user_message,raw_answer)

    answer=humanize_response(user_message,raw_answer,{})
    answer=enforce_no_identity_in_normal_chat(user_message,answer)
    answer=sanitize_final_output(user_message,answer)
    answer=final_conversation_guard(user_message,answer)

    add_event(trace,"humanized",module,function,raw_answer,answer)

    duplicate=should_block_duplicate(sender_id,answer)

    if duplicate:
        add_event(trace,"duplicate_blocked",module,function,answer,"")
        save_trace(trace)
        return ""

    msgs=split_human_reply(answer,{})
    final="\n\n".join(msgs[:4])

    add_event(trace,"final_output",module,function,answer,final)
    save_trace(trace)
    log_event(sender_id,user_message,final,kind="real")

    return final


